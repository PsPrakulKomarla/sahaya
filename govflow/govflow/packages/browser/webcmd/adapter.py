"""WebcmdBrowserAgent - BrowserAgent adapter for webcmd.

This adapter translates the BrowserAgent interface to webcmd CLI calls.
Only this layer contains webcmd-specific implementation details.

webcmd is invoked via subprocess calls to its CLI interface.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

from packages.browser.interfaces.agent import BrowserAgent, BrowserConfig, BrowserResult
from packages.browser.interfaces.models import (
    BrowserActionType,
    BrowserEvent,
    BrowserEventType,
    ElementType,
    PageModel,
    SemanticElement,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def _parse_elements_from_state(state_data: Dict[str, Any]) -> List[SemanticElement]:
    """Parse webcmd browser state into SemanticElement objects."""
    elements = []
    items = state_data.get("elements", state_data.get("items", []))

    for item in items:
        role_str = item.get("role", item.get("type", "unknown"))
        try:
            role = ElementType(role_str.lower())
        except ValueError:
            role = ElementType.UNKNOWN

        element = SemanticElement(
            element_id=item.get("id"),
            role=role,
            text=item.get("text", ""),
            label=item.get("label", item.get("aria-label", "")),
            description=item.get("description", item.get("title", "")),
            visible=item.get("visible", True),
            enabled=item.get("enabled", True),
            selector_hint=item.get("selector"),
            aria_label=item.get("aria-label"),
            placeholder=item.get("placeholder"),
            input_type=item.get("inputType", item.get("input-type")),
            href=item.get("href"),
            attributes={k: v for k, v in item.items() if k not in ("id", "role", "text", "label")},
        )
        elements.append(element)

    return elements


class WebcmdBrowserAgent(BrowserAgent):
    """BrowserAgent implementation backed by webcmd CLI.

    This adapter wraps webcmd subprocess calls and translates output
    into the normalized PageModel/SemanticElement format.

    webcmd CLI reference:
    - session create/close
    - browser open <url>
    - browser state (inspect DOM)
    - browser snapshot --snapshot-mode act|tree|read
    - browser click/find/type/select/upload
    - browser screenshot
    - browser back
    - browser scroll
    """

    def __init__(
        self,
        profile: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout: int = 60,
    ):
        self._profile = profile
        self._session_id = session_id
        self._timeout = timeout
        self._current_url_value: str = ""
        self._is_open = False
        self._events: List[BrowserEvent] = []

    @property
    def events(self) -> List[BrowserEvent]:
        return list(self._events)

    def _record_event(
        self,
        event_type: BrowserEventType,
        url: Optional[str] = None,
        action: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._events.append(
            BrowserEvent(
                event_type=event_type,
                url=url or self._current_url_value,
                action=action,
                success=success,
                error=error,
                metadata=kwargs,
            )
        )

    async def _run_webcmd(self, *args: str) -> Dict[str, Any]:
        """Execute a webcmd command and return parsed JSON output."""
        cmd = ["webcmd"]
        if self._profile:
            cmd.extend(["--profile", self._profile])
        if self._session_id:
            cmd.extend(["--session", self._session_id])
        cmd.extend(args)
        cmd.extend(["-f", "json"])

        logger.debug("webcmd_executing", command=" ".join(cmd))

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self._timeout
            )
            output = stdout.decode("utf-8").strip()
            if proc.returncode != 0:
                error_msg = stderr.decode("utf-8").strip()
                logger.error("webcmd_error", returncode=proc.returncode, stderr=error_msg)
                return {"error": error_msg, "returncode": proc.returncode}

            if output:
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"raw_output": output}
            return {}

        except asyncio.TimeoutError:
            logger.error("webcmd_timeout", command=" ".join(cmd))
            return {"error": "Command timed out"}
        except FileNotFoundError:
            logger.error("webcmd_not_found")
            return {"error": "webcmd not found. Install with: npm install -g @agentrhq/webcmd"}

    async def open(self, config: Optional[BrowserConfig] = None) -> BrowserResult:
        """Create a webcmd session and prepare for browser operations."""
        if not self._session_id:
            result = await self._run_webcmd("session", "create")
            if "error" in result:
                return BrowserResult(success=False, error=result["error"])
            self._session_id = result.get("sessionId", result.get("session_id", ""))

        self._is_open = True
        self._record_event(BrowserEventType.BROWSER_STARTED)
        return BrowserResult(success=True, data={"session_id": self._session_id})

    async def close(self) -> BrowserResult:
        """Close the webcmd session."""
        if self._session_id:
            await self._run_webcmd("session", "close", self._session_id)
        self._is_open = False
        self._session_id = None
        self._current_url_value = ""
        return BrowserResult(success=True)

    async def navigate(self, url: str) -> BrowserResult:
        """Navigate to a URL using webcmd browser open."""
        self._current_url_value = url
        result = await self._run_webcmd("browser", "open", url)
        if "error" in result:
            self._record_event(
                BrowserEventType.ACTION_FAILED,
                url=url,
                action="navigate",
                success=False,
                error=result["error"],
            )
            return BrowserResult(success=False, error=result["error"])

        self._record_event(BrowserEventType.PAGE_LOADED, url=url)

        page = await self.inspect()
        return BrowserResult(success=True, page=page)

    async def current_url(self) -> str:
        return self._current_url_value

    async def inspect(self) -> PageModel:
        """Inspect the current page using webcmd browser state."""
        result = await self._run_webcmd("browser", "state")
        if "error" in result:
            return PageModel(url=self._current_url_value, title="")

        elements = _parse_elements_from_state(result)
        title = result.get("title", "")
        text = result.get("text", "")
        url = result.get("url", self._current_url_value)

        self._record_event(BrowserEventType.PAGE_INSPECTED)

        return PageModel(
            url=url,
            title=title,
            text=text,
            elements=elements,
            metadata={"source": "webcmd"},
        )

    async def find_element(
        self,
        role: Optional[str] = None,
        text: Optional[str] = None,
        selector: Optional[str] = None,
    ) -> Optional[SemanticElement]:
        """Find a single element using webcmd browser find."""
        args = ["browser", "find"]
        if text:
            args.extend(["--text", text])
        if role:
            args.extend(["--role", role])
        if selector:
            args.extend(["--selector", selector])

        result = await self._run_webcmd(*args)
        if "error" in result or not result:
            return None

        items = result.get("matches", result.get("elements", []))
        if not items:
            return None

        item = items[0] if isinstance(items, list) else items
        role_str = item.get("role", "unknown")
        try:
            element_role = ElementType(role_str.lower())
        except ValueError:
            element_role = ElementType.UNKNOWN

        return SemanticElement(
            element_id=item.get("id"),
            role=element_role,
            text=item.get("text", ""),
            label=item.get("label", ""),
            description=item.get("description", ""),
            visible=item.get("visible", True),
            enabled=item.get("enabled", True),
            selector_hint=item.get("selector"),
        )

    async def click(self, target: str, selector: Optional[str] = None) -> BrowserResult:
        """Click an element using webcmd browser click."""
        args = ["browser", "click", target]
        if selector:
            args.extend(["--selector", selector])

        result = await self._run_webcmd(*args)
        if "error" in result:
            self._record_event(
                BrowserEventType.ACTION_FAILED,
                action="click",
                success=False,
                error=result["error"],
            )
            return BrowserResult(success=False, error=result["error"])

        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="click",
            element_text=target,
        )
        return BrowserResult(success=True, data={"clicked": target})

    async def type_text(
        self, target: str, text: str, selector: Optional[str] = None
    ) -> BrowserResult:
        """Type text using webcmd browser type."""
        args = ["browser", "type", target, text]
        if selector:
            args.extend(["--selector", selector])

        result = await self._run_webcmd(*args)
        if "error" in result:
            self._record_event(
                BrowserEventType.ACTION_FAILED,
                action="type",
                success=False,
                error=result["error"],
            )
            return BrowserResult(success=False, error=result["error"])

        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="type",
            element_text=target,
        )
        return BrowserResult(success=True, data={"typed": text})

    async def select(
        self, target: str, value: str, selector: Optional[str] = None
    ) -> BrowserResult:
        """Select an option using webcmd browser select."""
        args = ["browser", "select", target, value]
        if selector:
            args.extend(["--selector", selector])

        result = await self._run_webcmd(*args)
        if "error" in result:
            return BrowserResult(success=False, error=result["error"])

        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="select",
            element_text=target,
        )
        return BrowserResult(success=True, data={"selected": value})

    async def upload(
        self, target: str, file_path: str, selector: Optional[str] = None
    ) -> BrowserResult:
        """Upload a file using webcmd browser upload."""
        args = ["browser", "upload", target, file_path]
        if selector:
            args.extend(["--selector", selector])

        result = await self._run_webcmd(*args)
        if "error" in result:
            return BrowserResult(success=False, error=result["error"])

        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="upload",
            element_text=target,
        )
        return BrowserResult(success=True, data={"uploaded": file_path})

    async def extract_text(self) -> str:
        """Extract page text using webcmd browser snapshot --snapshot-mode read."""
        result = await self._run_webcmd("browser", "snapshot", "--snapshot-mode", "read")
        if "error" in result:
            return ""
        return result.get("text", result.get("snapshot", ""))

    async def extract_structured_data(self) -> Dict[str, Any]:
        """Extract structured data using webcmd browser state."""
        result = await self._run_webcmd("browser", "state")
        if "error" in result:
            return {}
        return result

    async def wait(self, seconds: float) -> BrowserResult:
        """Wait using webcmd browser wait."""
        await self._run_webcmd("browser", "wait", str(int(seconds)))
        return BrowserResult(success=True)

    async def screenshot(self, path: Optional[str] = None) -> BrowserResult:
        """Take a screenshot using webcmd browser screenshot."""
        result = await self._run_webcmd("browser", "screenshot")
        if "error" in result:
            return BrowserResult(success=False, error=result["error"])
        return BrowserResult(
            success=True,
            data={"path": path or result.get("path", "screenshot.png")},
        )

    async def go_back(self) -> BrowserResult:
        """Navigate back using webcmd browser back."""
        result = await self._run_webcmd("browser", "back")
        if "error" in result:
            return BrowserResult(success=False, error=result["error"])
        return BrowserResult(success=True)

    async def scroll(self, direction: str = "down", amount: int = 3) -> BrowserResult:
        """Scroll using webcmd browser scroll."""
        result = await self._run_webcmd("browser", "scroll", direction, str(amount))
        if "error" in result:
            return BrowserResult(success=False, error=result["error"])
        return BrowserResult(success=True)

    async def is_visible(self, target: str, selector: Optional[str] = None) -> bool:
        """Check visibility using webcmd browser find."""
        element = await self.find_element(text=target, selector=selector)
        return element is not None and element.visible

    async def get_page_title(self) -> str:
        """Get page title using webcmd browser state."""
        result = await self._run_webcmd("browser", "state")
        return result.get("title", "")
