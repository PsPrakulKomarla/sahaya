"""PlaywrightBrowserAgent — real browser implementation of BrowserAgent.

This proves the BrowserAgent interface works with a real browser engine.
Currently for testing against local test pages only — NOT for production use.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from packages.browser.interfaces.agent import BrowserAgent, BrowserConfig, BrowserResult
from packages.browser.interfaces.models import (
    BrowserEvent,
    BrowserEventType,
    ElementType,
    PageModel,
    SemanticElement,
)


class PlaywrightBrowserAgent(BrowserAgent):
    """Real browser implementation using Playwright.

    For testing against local test pages only.
    Production implementation will use webcmd.
    """

    def __init__(self) -> None:
        self._browser = None
        self._page = None
        self._context = None
        self._playwright = None
        self._current_url = ""
        self._events: List[BrowserEvent] = []

    async def open(self, config: Optional[BrowserConfig] = None) -> BrowserResult:
        config = config or BrowserConfig()
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return BrowserResult(
                success=False,
                error="Playwright not installed. Run: pip install playwright && playwright install",
            )

        self._playwright = await async_playwright().start()
        browser_type = self._playwright.chromium
        self._browser = await browser_type.launch(headless=config.headless)
        self._context = await self._browser.new_context(
            viewport={"width": config.viewport_width, "height": config.viewport_height},
            user_agent=config.user_agent,
        )
        self._page = await self._context.new_page()
        self._record_event(BrowserEventType.BROWSER_STARTED)
        return BrowserResult(success=True)

    async def close(self) -> BrowserResult:
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
        return BrowserResult(success=True)

    async def navigate(self, url: str) -> BrowserResult:
        if not self._page:
            return BrowserResult(success=False, error="Browser not open")
        try:
            await self._page.goto(url, wait_until="domcontentloaded")
            self._current_url = url
            self._record_event(BrowserEventType.PAGE_LOADED, url=url)
            page = await self.inspect()
            return BrowserResult(success=True, page=page)
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    async def current_url(self) -> str:
        if self._page:
            return self._page.url
        return self._current_url

    async def inspect(self) -> PageModel:
        if not self._page:
            return PageModel()
        try:
            title = await self._page.title()
            url = self._page.url
            text = await self._page.inner_text("body")
            elements = await self._extract_elements()
            self._record_event(BrowserEventType.PAGE_INSPECTED)
            return PageModel(
                url=url,
                title=title,
                text=text[:5000],
                elements=elements,
            )
        except Exception:
            return PageModel(url=self._current_url)

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
        if not self._page:
            return BrowserResult(success=False, error="Browser not open")
        try:
            if selector:
                await self._page.click(selector)
            else:
                await self._page.get_by_text(target).first.click()
            self._record_event(BrowserEventType.ACTION_COMPLETED, action="click")
            return BrowserResult(success=True, data={"clicked": target})
        except Exception as e:
            self._record_event(BrowserEventType.ACTION_FAILED, action="click")
            return BrowserResult(success=False, error=str(e))

    async def type_text(
        self, target: str, text: str, selector: Optional[str] = None
    ) -> BrowserResult:
        if not self._page:
            return BrowserResult(success=False, error="Browser not open")
        try:
            if selector:
                await self._page.fill(selector, text)
            else:
                await self._page.get_by_label(target).first.fill(text)
            self._record_event(BrowserEventType.ACTION_COMPLETED, action="type")
            return BrowserResult(success=True, data={"typed": text})
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    async def select(
        self, target: str, value: str, selector: Optional[str] = None
    ) -> BrowserResult:
        if not self._page:
            return BrowserResult(success=False, error="Browser not open")
        try:
            if selector:
                await self._page.select_option(selector, value)
            else:
                await self._page.get_by_label(target).first.select_option(value)
            self._record_event(BrowserEventType.ACTION_COMPLETED, action="select")
            return BrowserResult(success=True, data={"selected": value})
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    async def upload(
        self, target: str, file_path: str, selector: Optional[str] = None
    ) -> BrowserResult:
        if not self._page:
            return BrowserResult(success=False, error="Browser not open")
        try:
            if selector:
                await self._page.set_input_files(selector, file_path)
            else:
                await self._page.get_by_label(target).first.set_input_files(file_path)
            self._record_event(BrowserEventType.ACTION_COMPLETED, action="upload")
            return BrowserResult(success=True, data={"uploaded": file_path})
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    async def extract_text(self) -> str:
        if not self._page:
            return ""
        try:
            return await self._page.inner_text("body")
        except Exception:
            return ""

    async def extract_structured_data(self) -> Dict[str, Any]:
        page = await self.inspect()
        return {
            "url": page.url,
            "title": page.title,
            "text": page.text[:2000],
            "element_count": len(page.elements),
        }

    async def wait(self, seconds: float) -> BrowserResult:
        if self._page:
            await self._page.wait_for_timeout(int(seconds * 1000))
        return BrowserResult(success=True)

    async def screenshot(self, path: Optional[str] = None) -> BrowserResult:
        if not self._page:
            return BrowserResult(success=False, error="Browser not open")
        try:
            screenshot_path = path or "/tmp/playwright_screenshot.png"
            await self._page.screenshot(path=screenshot_path)
            self._record_event(BrowserEventType.ACTION_COMPLETED, action="screenshot")
            return BrowserResult(success=True, data={"screenshot_path": screenshot_path})
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    async def go_back(self) -> BrowserResult:
        if self._page:
            await self._page.go_back()
            self._current_url = self._page.url
        return BrowserResult(success=True)

    async def scroll(self, direction: str = "down", amount: int = 3) -> BrowserResult:
        if self._page:
            delta = amount * 100 if direction == "down" else -(amount * 100)
            await self._page.mouse.wheel(0, delta)
        return BrowserResult(success=True)

    async def is_visible(self, target: str, selector: Optional[str] = None) -> bool:
        if not self._page:
            return False
        try:
            if selector:
                return await self._page.is_visible(selector)
            return await self._page.get_by_text(target).first.is_visible()
        except Exception:
            return False

    async def get_page_title(self) -> str:
        if self._page:
            return await self._page.title()
        return ""

    async def _extract_elements(self) -> List[SemanticElement]:
        """Extract semantic elements from the page."""
        if not self._page:
            return []
        elements = []
        try:
            buttons = await self._page.query_selector_all("button, [role='button']")
            for btn in buttons[:20]:
                text = await btn.inner_text()
                elements.append(SemanticElement(
                    role=ElementType.BUTTON,
                    text=text.strip(),
                    visible=await btn.is_visible(),
                ))

            inputs = await self._page.query_selector_all("input, textarea")
            for inp in inputs[:20]:
                label = await inp.get_attribute("aria-label") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                elements.append(SemanticElement(
                    role=ElementType.INPUT,
                    label=label or placeholder,
                    placeholder=placeholder,
                    visible=await inp.is_visible(),
                ))

            links = await self._page.query_selector_all("a[href]")
            for link in links[:20]:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                elements.append(SemanticElement(
                    role=ElementType.LINK,
                    text=text.strip(),
                    href=href,
                    visible=await link.is_visible(),
                ))
        except Exception:
            pass
        return elements

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
