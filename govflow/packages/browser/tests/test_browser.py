"""Tests for browser abstraction — MockBrowserAgent and PlaywrightBrowserAgent."""
import pytest
from packages.browser.mock.agent import MockBrowserAgent
from packages.browser.interfaces.agent import BrowserConfig, BrowserResult
from packages.browser.interfaces.models import ElementType, PageModel


class TestMockBrowserAgent:
    @pytest.mark.asyncio
    async def test_open_and_close(self):
        agent = MockBrowserAgent()
        result = await agent.open()
        assert result.success is True

        result = await agent.close()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_navigate(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.navigate("https://example.gov.in")
        assert result.success is True
        assert result.page is not None
        assert result.page.url == "https://example.gov.in"

    @pytest.mark.asyncio
    async def test_current_url(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://example.gov.in")
        url = await agent.current_url()
        assert url == "https://example.gov.in"

    @pytest.mark.asyncio
    async def test_inspect(self):
        agent = MockBrowserAgent()
        await agent.open()
        page = await agent.inspect()
        assert isinstance(page, PageModel)
        assert len(page.elements) > 0

    @pytest.mark.asyncio
    async def test_find_element(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://example.gov.in")
        element = await agent.find_element(text="Apply Now")
        assert element is not None
        assert element.role == ElementType.BUTTON

    @pytest.mark.asyncio
    async def test_click(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.click("Apply Now")
        assert result.success is True
        assert "Apply Now" in agent.get_clicked_elements()

    @pytest.mark.asyncio
    async def test_type_text(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.type_text("Full Name", "John Doe")
        assert result.success is True
        assert agent.get_filled_forms()["Full Name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_select(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.select("State", "Karnataka")
        assert result.success is True
        assert agent.get_filled_forms()["State"] == "Karnataka"

    @pytest.mark.asyncio
    async def test_upload(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.upload("Document", "/tmp/test.pdf")
        assert result.success is True
        assert "/tmp/test.pdf" in agent.get_uploaded_files()

    @pytest.mark.asyncio
    async def test_extract_text(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://example.gov.in")
        text = await agent.extract_text()
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_extract_structured_data(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://example.gov.in")
        data = await agent.extract_structured_data()
        assert "url" in data
        assert "title" in data

    @pytest.mark.asyncio
    async def test_screenshot(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.screenshot()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_go_back(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://page1.gov.in")
        await agent.navigate("https://page2.gov.in")
        await agent.go_back()
        url = await agent.current_url()
        assert url == "https://page1.gov.in"

    @pytest.mark.asyncio
    async def test_scroll(self):
        agent = MockBrowserAgent()
        await agent.open()
        result = await agent.scroll("down", 5)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_is_visible(self):
        agent = MockBrowserAgent()
        await agent.open()
        visible = await agent.is_visible("Apply Now")
        assert visible is True

    @pytest.mark.asyncio
    async def test_get_page_title(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://example.gov.in")
        title = await agent.get_page_title()
        assert len(title) > 0

    @pytest.mark.asyncio
    async def test_events_recorded(self):
        agent = MockBrowserAgent()
        await agent.open()
        await agent.navigate("https://example.gov.in")
        await agent.click("Apply Now")
        events = agent.get_events()
        assert len(events) >= 2

    @pytest.mark.asyncio
    async def test_context_manager(self):
        agent = MockBrowserAgent()
        async with agent:
            url = await agent.current_url()
            assert url == "about:blank"


class TestBrowserProviderExtensibility:
    """Test that both MockBrowserAgent and PlaywrightBrowserAgent
    implement the same BrowserAgent interface."""

    def test_mock_implements_interface(self):
        from packages.browser.interfaces.agent import BrowserAgent
        assert issubclass(MockBrowserAgent, BrowserAgent)

    def test_playwright_implements_interface(self):
        from packages.browser.interfaces.agent import BrowserAgent
        from packages.browser.playwright.agent import PlaywrightBrowserAgent
        assert issubclass(PlaywrightBrowserAgent, BrowserAgent)

    def test_mock_has_all_methods(self):
        agent = MockBrowserAgent()
        methods = [
            "open", "close", "navigate", "current_url", "inspect",
            "find_element", "click", "type_text", "select", "upload",
            "extract_text", "extract_structured_data", "wait",
            "screenshot", "go_back", "scroll", "is_visible", "get_page_title",
        ]
        for method in methods:
            assert hasattr(agent, method), f"Missing method: {method}"


class TestPageModel:
    def test_find_elements_by_role(self):
        page = PageModel(elements=[
            __import__("packages.browser.interfaces.models", fromlist=["SemanticElement"]).SemanticElement(
                role=ElementType.BUTTON, text="Click me"
            ),
            __import__("packages.browser.interfaces.models", fromlist=["SemanticElement"]).SemanticElement(
                role=ElementType.INPUT, text="Name"
            ),
        ])
        buttons = page.find_elements(role=ElementType.BUTTON)
        assert len(buttons) == 1
        assert buttons[0].text == "Click me"

    def test_find_elements_by_text(self):
        page = PageModel(elements=[
            __import__("packages.browser.interfaces.models", fromlist=["SemanticElement"]).SemanticElement(
                role=ElementType.BUTTON, text="Apply Now"
            ),
        ])
        found = page.find_elements(text="Apply")
        assert len(found) == 1

    def test_find_element(self):
        page = PageModel(elements=[
            __import__("packages.browser.interfaces.models", fromlist=["SemanticElement"]).SemanticElement(
                role=ElementType.BUTTON, text="Submit"
            ),
        ])
        el = page.find_element(role=ElementType.BUTTON)
        assert el is not None

    def test_has_element(self):
        page = PageModel(elements=[
            __import__("packages.browser.interfaces.models", fromlist=["SemanticElement"]).SemanticElement(
                role=ElementType.BUTTON, text="Submit"
            ),
        ])
        assert page.has_element(text="Submit")
        assert not page.has_element(text="Cancel")
