"""MockBrowserAgent for testing.

Simulates browser operations using controlled test data.
Does NOT connect to real government websites.
"""
from __future__ import annotations

import asyncio
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


MOCK_TEST_PAGE = PageModel(
    url="https://example.gov.in/test",
    title="Mock Government Portal",
    text="Welcome to the Government Service Portal. Apply for certificates, track applications, and more.",
    elements=[
        SemanticElement(
            role=ElementType.BUTTON,
            text="Apply Now",
            label="Start new application",
            description="Begin a new application for a government service",
        ),
        SemanticElement(
            role=ElementType.BUTTON,
            text="Track Application",
            label="Track your application",
            description="Check the status of an existing application",
        ),
        SemanticElement(
            role=ElementType.INPUT,
            text="Full Name",
            label="Full Name",
            placeholder="Enter your full name",
            input_type="text",
        ),
        SemanticElement(
            role=ElementType.INPUT,
            text="Email",
            label="Email Address",
            placeholder="Enter your email",
            input_type="email",
        ),
        SemanticElement(
            role=ElementType.SELECT,
            text="State",
            label="Select State",
            options=["Karnataka", "Maharashtra", "Tamil Nadu", "Kerala"],
        ),
        SemanticElement(
            role=ElementType.LINK,
            text="Home",
            href="https://example.gov.in/",
        ),
        SemanticElement(
            role=ElementType.HEADING,
            text="Government Service Portal",
        ),
    ],
    metadata={"mock": True},
)


class MockBrowserAgent(BrowserAgent):
    """Mock browser agent for testing.

    Simulates navigation, inspection, clicking, typing, and extraction
    using controlled test data.
    """

    def __init__(self) -> None:
        self._is_open = False
        self._current_url = ""
        self._current_page: Optional[PageModel] = None
        self._events: List[BrowserEvent] = []
        self._history: List[str] = []
        self._filled_forms: Dict[str, str] = {}
        self._clicked_elements: List[str] = []
        self._uploaded_files: List[str] = []
        self._screenshots: List[str] = []

    async def open(self, config: Optional[BrowserConfig] = None) -> BrowserResult:
        self._is_open = True
        self._current_url = "about:blank"
        self._record_event(BrowserEventType.BROWSER_STARTED)
        return BrowserResult(success=True, page=PageModel(url="about:blank", title="Blank"))

    async def close(self) -> BrowserResult:
        self._is_open = False
        self._current_url = ""
        self._current_page = None
        return BrowserResult(success=True)

    async def navigate(self, url: str) -> BrowserResult:
        self._history.append(self._current_url)
        self._current_url = url
        self._current_page = PageModel(
            url=url,
            title=f"Page at {url}",
            text=f"Content of {url}",
            elements=MOCK_TEST_PAGE.elements.copy(),
            metadata={"mock": True},
        )
        self._record_event(BrowserEventType.PAGE_LOADED, url=url)
        return BrowserResult(success=True, page=self._current_page)

    async def current_url(self) -> str:
        return self._current_url

    async def inspect(self) -> PageModel:
        if self._current_page is None:
            self._current_page = MOCK_TEST_PAGE.model_copy()
            self._current_page.url = self._current_url
        self._record_event(BrowserEventType.PAGE_INSPECTED)
        return self._current_page

    async def find_element(
        self,
        role: Optional[str] = None,
        text: Optional[str] = None,
        selector: Optional[str] = None,
    ) -> Optional[SemanticElement]:
        page = await self.inspect()
        element_role = None
        if role:
            try:
                element_role = ElementType(role)
            except ValueError:
                pass
        return page.find_element(role=element_role, text=text)

    async def click(self, target: str, selector: Optional[str] = None) -> BrowserResult:
        self._clicked_elements.append(target)
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="click",
        )
        return BrowserResult(
            success=True,
            data={"clicked": target},
        )

    async def type_text(
        self, target: str, text: str, selector: Optional[str] = None
    ) -> BrowserResult:
        self._filled_forms[target] = text
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="type",
        )
        return BrowserResult(
            success=True,
            data={"typed": text, "target": target},
        )

    async def select(
        self, target: str, value: str, selector: Optional[str] = None
    ) -> BrowserResult:
        self._filled_forms[target] = value
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="select",
        )
        return BrowserResult(
            success=True,
            data={"selected": value, "target": target},
        )

    async def upload(
        self, target: str, file_path: str, selector: Optional[str] = None
    ) -> BrowserResult:
        self._uploaded_files.append(file_path)
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="upload",
        )
        return BrowserResult(
            success=True,
            data={"uploaded": file_path, "target": target},
        )

    async def extract_text(self) -> str:
        page = await self.inspect()
        return page.text

    async def extract_structured_data(self) -> Dict[str, Any]:
        page = await self.inspect()
        return {
            "url": page.url,
            "title": page.title,
            "text": page.text,
            "element_count": len(page.elements),
        }

    async def wait(self, seconds: float) -> BrowserResult:
        await asyncio.sleep(min(seconds, 0.01))
        return BrowserResult(success=True)

    async def screenshot(self, path: Optional[str] = None) -> BrowserResult:
        screenshot_path = path or f"/tmp/mock_screenshot_{len(self._screenshots)}.png"
        self._screenshots.append(screenshot_path)
        self._record_event(
            BrowserEventType.ACTION_COMPLETED,
            action="screenshot",
        )
        return BrowserResult(
            success=True,
            data={"screenshot_path": screenshot_path},
        )

    async def go_back(self) -> BrowserResult:
        if self._history:
            self._current_url = self._history.pop()
        return BrowserResult(success=True)

    async def scroll(self, direction: str = "down", amount: int = 3) -> BrowserResult:
        return BrowserResult(
            success=True,
            data={"direction": direction, "amount": amount},
        )

    async def is_visible(self, target: str, selector: Optional[str] = None) -> bool:
        return True

    async def get_page_title(self) -> str:
        page = await self.inspect()
        return page.title

    def get_filled_forms(self) -> Dict[str, str]:
        return dict(self._filled_forms)

    def get_clicked_elements(self) -> List[str]:
        return list(self._clicked_elements)

    def get_uploaded_files(self) -> List[str]:
        return list(self._uploaded_files)

    def get_events(self) -> List[BrowserEvent]:
        return list(self._events)

    def _record_event(
        self,
        event_type: BrowserEventType,
        url: Optional[str] = None,
        action: Optional[str] = None,
    ) -> None:
        self._events.append(
            BrowserEvent(
                event_type=event_type,
                url=url or self._current_url,
                action=action,
            )
        )
