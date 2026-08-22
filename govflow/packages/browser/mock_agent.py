"""MockBrowserAgent for testing.

Provides a simulated browser that can be configured with predefined page
responses. Used for unit testing the learning pipeline, workflow memory,
and recovery engine without requiring a real browser.
"""

from __future__ import annotations

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


class MockBrowserAgent(BrowserAgent):
    """A mock browser agent for testing.

    Pre-load pages using ``add_page`` and the mock will return them
    when ``navigate`` or ``inspect`` is called.
    """

    def __init__(self) -> None:
        self._pages: Dict[str, PageModel] = {}
        self._current_url: str = ""
        self._current_page: Optional[PageModel] = None
        self._history: List[str] = []
        self._is_open: bool = False
        self._events: List[BrowserEvent] = []
        self._config: Optional[BrowserConfig] = None
        self._action_log: List[Dict[str, Any]] = []

    def add_page(self, url: str, page: PageModel) -> None:
        """Register a page to be returned for a given URL."""
        self._pages[url] = page

    def add_page_with_elements(
        self,
        url: str,
        title: str,
        elements: List[SemanticElement],
        text: str = "",
    ) -> None:
        """Convenience method to register a page with elements."""
        self._pages[url] = PageModel(
            url=url,
            title=title,
            text=text or title,
            elements=elements,
        )

    @property
    def events(self) -> List[BrowserEvent]:
        return list(self._events)

    @property
    def action_log(self) -> List[Dict[str, Any]]:
        return list(self._action_log)

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
                url=url or self._current_url,
                action=action,
                success=success,
                error=error,
                metadata=kwargs,
            )
        )

    async def open(self, config: Optional[BrowserConfig] = None) -> BrowserResult:
        self._is_open = True
        self._config = config
        self._record_event(BrowserEventType.BROWSER_STARTED)
        return BrowserResult(success=True)

    async def close(self) -> BrowserResult:
        self._is_open = False
        self._current_url = ""
        self._current_page = None
        return BrowserResult(success=True)

    async def navigate(self, url: str) -> BrowserResult:
        self._history.append(self._current_url)
        self._current_url = url
        self._current_page = self._pages.get(url)
        self._action_log.append({"action": "navigate", "url": url})
        self._record_event(BrowserEventType.PAGE_LOADED, url=url)
        return BrowserResult(
            success=True,
            page=self._current_page,
        )

    async def current_url(self) -> str:
        return self._current_url

    async def inspect(self) -> PageModel:
        self._record_event(BrowserEventType.PAGE_INSPECTED)
        if self._current_page:
            return self._current_page
        return PageModel(url=self._current_url, title="")

    async def find_element(
        self,
        role: Optional[str] = None,
        text: Optional[str] = None,
        selector: Optional[str] = None,
    ) -> Optional[SemanticElement]:
        if not self._current_page:
            return None
        element_role = ElementType(role) if role else None
        return self._current_page.find_element(role=element_role, text=text)

    async def click(self, target: str, selector: Optional[str] = None) -> BrowserResult:
        self._action_log.append({"action": "click", "target": target, "selector": selector})
        element = None
        if self._current_page:
            element = self._current_page.find_element(text=target)
        if element:
            self._record_event(
                BrowserEventType.ACTION_COMPLETED,
                action="click",
                element_text=target,
            )
            return BrowserResult(success=True, data={"clicked": target})
        self._record_event(
            BrowserEventType.ACTION_FAILED,
            action="click",
            success=False,
            error=f"Element not found: {target}",
        )
        return BrowserResult(success=False, error=f"Element not found: {target}")

    async def type_text(
        self, target: str, text: str, selector: Optional[str] = None
    ) -> BrowserResult:
        self._action_log.append({"action": "type", "target": target, "text": text})
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="type",
            element_text=target,
        )
        return BrowserResult(success=True, data={"typed": text, "target": target})

    async def select(
        self, target: str, value: str, selector: Optional[str] = None
    ) -> BrowserResult:
        self._action_log.append({"action": "select", "target": target, "value": value})
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="select",
            element_text=target,
        )
        return BrowserResult(success=True, data={"selected": value, "target": target})

    async def upload(
        self, target: str, file_path: str, selector: Optional[str] = None
    ) -> BrowserResult:
        self._action_log.append({"action": "upload", "target": target, "file_path": file_path})
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="upload",
            element_text=target,
        )
        return BrowserResult(success=True, data={"uploaded": file_path})

    async def extract_text(self) -> str:
        if self._current_page:
            return self._current_page.text
        return ""

    async def extract_structured_data(self) -> Dict[str, Any]:
        if self._current_page:
            return {
                "url": self._current_page.url,
                "title": self._current_page.title,
                "text": self._current_page.text,
                "element_count": len(self._current_page.elements),
            }
        return {}

    async def wait(self, seconds: float) -> BrowserResult:
        return BrowserResult(success=True)

    async def screenshot(self, path: Optional[str] = None) -> BrowserResult:
        return BrowserResult(success=True, data={"path": path or "mock_screenshot.png"})

    async def go_back(self) -> BrowserResult:
        if self._history:
            self._current_url = self._history.pop()
            self._current_page = self._pages.get(self._current_url)
        return BrowserResult(success=True)

    async def scroll(self, direction: str = "down", amount: int = 3) -> BrowserResult:
        self._action_log.append({"action": "scroll", "direction": direction, "amount": amount})
        return BrowserResult(success=True)

    async def is_visible(self, target: str, selector: Optional[str] = None) -> bool:
        if self._current_page:
            element = self._current_page.find_element(text=target)
            return element is not None and element.visible
        return False

    async def get_page_title(self) -> str:
        if self._current_page:
            return self._current_page.title
        return ""
