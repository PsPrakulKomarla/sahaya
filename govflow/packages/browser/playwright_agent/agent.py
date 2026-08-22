from typing import Optional
from packages.browser.interfaces.agent import BrowserAgent
from packages.browser.interfaces.models import (
    BrowserAction,
    BrowserActionType,
    BrowserActionResult,
    PageInfo,
    ElementTarget,
)


class PlaywrightBrowserAgent(BrowserAgent):
    """Playwright-based browser agent.

    Uses Playwright for real browser automation.
    Should only be used against controlled test pages during development.
    """

    def __init__(self, headless: bool = True):
        self._headless = headless
        self._playwright = None
        self._browser = None
        self._page = None
        self._is_open = False

    async def open(self) -> None:
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self._headless)
            self._page = await self._browser.new_page()
            self._is_open = True
        except ImportError:
            raise RuntimeError("Playwright is not installed. Install with: pip install playwright && playwright install")

    async def close(self) -> None:
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._is_open = False

    async def navigate(self, url: str) -> BrowserActionResult:
        if not self._page:
            return BrowserActionResult(success=False, action="NAVIGATE", error="Browser not open")
        await self._page.goto(url)
        return BrowserActionResult(success=True, action="NAVIGATE", url=url)

    async def current_url(self) -> str:
        if not self._page:
            return ""
        return self._page.url

    async def inspect(self) -> PageInfo:
        if not self._page:
            return PageInfo(url="", title="")
        title = await self._page.title()
        url = self._page.url
        content = await self._page.content()
        return PageInfo(url=url, title=title, content=content[:5000])

    async def execute_action(self, action: BrowserAction) -> BrowserActionResult:
        if not self._page:
            return BrowserActionResult(success=False, action=action.type.value, error="Browser not open")

        try:
            if action.type == BrowserActionType.NAVIGATE:
                return await self.navigate(action.url or "about:blank")

            elif action.type == BrowserActionType.CLICK:
                selector = self._resolve_selector(action.target)
                await self._page.click(selector)
                return BrowserActionResult(success=True, action="CLICK", target=selector)

            elif action.type == BrowserActionType.TYPE:
                selector = self._resolve_selector(action.target)
                await self._page.fill(selector, action.value or "")
                return BrowserActionResult(success=True, action="TYPE", target=selector)

            elif action.type == BrowserActionType.SELECT:
                selector = self._resolve_selector(action.target)
                await self._page.select_option(selector, action.value or "")
                return BrowserActionResult(success=True, action="SELECT", target=selector)

            elif action.type == BrowserActionType.EXTRACT_TEXT:
                text = await self._page.inner_text("body")
                return BrowserActionResult(success=True, action="EXTRACT_TEXT", data=text[:5000])

            elif action.type == BrowserActionType.EXTRACT_DATA:
                content = await self._page.content()
                return BrowserActionResult(success=True, action="EXTRACT_DATA", data=content[:5000])

            elif action.type == BrowserActionType.UPLOAD:
                selector = self._resolve_selector(action.target)
                if action.value:
                    await self._page.set_input_files(selector, action.value)
                return BrowserActionResult(success=True, action="UPLOAD", target=selector)

            elif action.type == BrowserActionType.WAIT:
                timeout = action.timeout_seconds * 1000
                await self._page.wait_for_load_state("networkidle", timeout=timeout)
                return BrowserActionResult(success=True, action="WAIT")

            elif action.type == BrowserActionType.SCROLL:
                await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                return BrowserActionResult(success=True, action="SCROLL")

            elif action.type == BrowserActionType.GO_BACK:
                await self._page.go_back()
                return BrowserActionResult(success=True, action="GO_BACK")

            elif action.type == BrowserActionType.IS_VISIBLE:
                selector = self._resolve_selector(action.target)
                visible = await self._page.is_visible(selector)
                return BrowserActionResult(success=True, action="IS_VISIBLE", data=visible)

            elif action.type == BrowserActionType.GET_PAGE_TITLE:
                title = await self._page.title()
                return BrowserActionResult(success=True, action="GET_PAGE_TITLE", data=title)

            elif action.type == BrowserActionType.SCREENSHOT:
                screenshot = await self._page.screenshot()
                return BrowserActionResult(success=True, action="SCREENSHOT", data=screenshot)

            elif action.type == BrowserActionType.FIND_ELEMENT:
                selector = self._resolve_selector(action.target)
                element = await self._page.query_selector(selector)
                return BrowserActionResult(
                    success=True,
                    action="FIND_ELEMENT",
                    data={"found": element is not None},
                )

            return BrowserActionResult(
                success=False,
                action=action.type.value,
                error=f"Unknown action type: {action.type}",
            )

        except Exception as e:
            return BrowserActionResult(
                success=False,
                action=action.type.value,
                error=str(e),
            )

    async def screenshot(self) -> bytes:
        if not self._page:
            return b""
        return await self._page.screenshot()

    async def is_available(self) -> bool:
        return self._is_open and self._page is not None

    def _resolve_selector(self, target: Optional[ElementTarget]) -> str:
        if target is None:
            return "body"
        if target.selector:
            return target.selector
        if target.text:
            return f"text={target.text}"
        if target.aria_label:
            return f"[aria-label='{target.aria_label}']"
        if target.role:
            return target.role
        return "body"
