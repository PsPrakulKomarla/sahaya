from typing import Optional, List, Dict, Any
from packages.browser.interfaces.agent import BrowserAgent
from packages.browser.interfaces.models import (
    BrowserAction,
    BrowserActionType,
    BrowserActionResult,
    PageInfo,
)


class MockBrowserAgent(BrowserAgent):
    """Mock browser agent for testing.

    Simulates browser interactions with controlled test data.
    Does NOT connect to any real websites.
    """

    def __init__(self):
        self._is_open = False
        self._current_url = "about:blank"
        self._page_title = "Mock Page"
        self._history: List[str] = ["about:blank"]
        self._actions_log: List[BrowserAction] = []
        self._mock_pages: Dict[str, PageInfo] = {
            "about:blank": PageInfo(
                url="about:blank",
                title="Blank Page",
                content="",
                elements=[],
            ),
        }
        self._mock_elements: Dict[str, Dict[str, Any]] = {}

    async def open(self) -> None:
        self._is_open = True

    async def close(self) -> None:
        self._is_open = False

    async def navigate(self, url: str) -> BrowserActionResult:
        self._current_url = url
        self._history.append(url)
        self._page_title = self._mock_pages.get(url, PageInfo(
            url=url, title=f"Page: {url}"
        )).title
        return BrowserActionResult(
            success=True,
            action="NAVIGATE",
            url=url,
        )

    async def current_url(self) -> str:
        return self._current_url

    async def inspect(self) -> PageInfo:
        return self._mock_pages.get(self._current_url, PageInfo(
            url=self._current_url,
            title=self._page_title,
            content="Mock page content",
            elements=[],
        ))

    async def execute_action(self, action: BrowserAction) -> BrowserActionResult:
        self._actions_log.append(action)

        if action.type == BrowserActionType.NAVIGATE:
            return await self.navigate(action.url or "about:blank")

        elif action.type == BrowserActionType.CLICK:
            return BrowserActionResult(
                success=True,
                action="CLICK",
                target=action.target.description if action.target else None,
                url=self._current_url,
            )

        elif action.type == BrowserActionType.TYPE:
            return BrowserActionResult(
                success=True,
                action="TYPE",
                target=action.target.description if action.target else None,
                url=self._current_url,
            )

        elif action.type == BrowserActionType.SELECT:
            return BrowserActionResult(
                success=True,
                action="SELECT",
                target=action.target.description if action.target else None,
                url=self._current_url,
            )

        elif action.type == BrowserActionType.EXTRACT_TEXT:
            return BrowserActionResult(
                success=True,
                action="EXTRACT_TEXT",
                data="Mock extracted text",
                url=self._current_url,
            )

        elif action.type == BrowserActionType.EXTRACT_DATA:
            return BrowserActionResult(
                success=True,
                action="EXTRACT_DATA",
                data={"mock_key": "mock_value"},
                url=self._current_url,
            )

        elif action.type == BrowserActionType.UPLOAD:
            return BrowserActionResult(
                success=True,
                action="UPLOAD",
                target=action.target.description if action.target else None,
                url=self._current_url,
            )

        elif action.type == BrowserActionType.WAIT:
            return BrowserActionResult(
                success=True,
                action="WAIT",
                url=self._current_url,
            )

        elif action.type == BrowserActionType.SCROLL:
            return BrowserActionResult(
                success=True,
                action="SCROLL",
                url=self._current_url,
            )

        elif action.type == BrowserActionType.GO_BACK:
            if len(self._history) > 1:
                self._history.pop()
                self._current_url = self._history[-1]
            return BrowserActionResult(
                success=True,
                action="GO_BACK",
                url=self._current_url,
            )

        elif action.type == BrowserActionType.IS_VISIBLE:
            return BrowserActionResult(
                success=True,
                action="IS_VISIBLE",
                data=True,
                url=self._current_url,
            )

        elif action.type == BrowserActionType.GET_PAGE_TITLE:
            return BrowserActionResult(
                success=True,
                action="GET_PAGE_TITLE",
                data=self._page_title,
                url=self._current_url,
            )

        elif action.type == BrowserActionType.SCREENSHOT:
            return BrowserActionResult(
                success=True,
                action="SCREENSHOT",
                data=b"mock_screenshot_bytes",
                url=self._current_url,
            )

        elif action.type == BrowserActionType.FIND_ELEMENT:
            return BrowserActionResult(
                success=True,
                action="FIND_ELEMENT",
                data={"found": True},
                url=self._current_url,
            )

        return BrowserActionResult(
            success=False,
            action=action.type.value,
            error=f"Unknown action type: {action.type}",
        )

    async def screenshot(self) -> bytes:
        return b"mock_screenshot"

    async def is_available(self) -> bool:
        return self._is_open

    def get_actions_log(self) -> List[BrowserAction]:
        return list(self._actions_log)

    def set_mock_page(self, url: str, page: PageInfo) -> None:
        self._mock_pages[url] = page
