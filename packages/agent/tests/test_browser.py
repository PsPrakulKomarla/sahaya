import pytest
from packages.browser.mock.mock_agent import MockBrowserAgent
from packages.browser.interfaces.models import (
    BrowserAction,
    BrowserActionType,
    ElementTarget,
    PageInfo,
)


class TestMockBrowserAgent:
    @pytest.fixture
    def agent(self):
        return MockBrowserAgent()

    @pytest.mark.asyncio
    async def test_open_close(self, agent):
        await agent.open()
        assert await agent.is_available() is True
        await agent.close()
        assert await agent.is_available() is False

    @pytest.mark.asyncio
    async def test_navigate(self, agent):
        await agent.open()
        result = await agent.navigate("https://example.gov.in")
        assert result.success is True
        assert result.url == "https://example.gov.in"
        assert await agent.current_url() == "https://example.gov.in"

    @pytest.mark.asyncio
    async def test_inspect(self, agent):
        await agent.open()
        page = await agent.inspect()
        assert page.url == "about:blank"

    @pytest.mark.asyncio
    async def test_click(self, agent):
        await agent.open()
        action = BrowserAction(
            type=BrowserActionType.CLICK,
            target=ElementTarget(description="Submit button"),
        )
        result = await agent.execute_action(action)
        assert result.success is True
        assert result.action == "CLICK"

    @pytest.mark.asyncio
    async def test_type(self, agent):
        await agent.open()
        action = BrowserAction(
            type=BrowserActionType.TYPE,
            target=ElementTarget(description="Name field"),
            value="John Doe",
        )
        result = await agent.execute_action(action)
        assert result.success is True
        assert result.action == "TYPE"

    @pytest.mark.asyncio
    async def test_extract_text(self, agent):
        await agent.open()
        action = BrowserAction(type=BrowserActionType.EXTRACT_TEXT)
        result = await agent.execute_action(action)
        assert result.success is True
        assert result.data == "Mock extracted text"

    @pytest.mark.asyncio
    async def test_extract_data(self, agent):
        await agent.open()
        action = BrowserAction(type=BrowserActionType.EXTRACT_DATA)
        result = await agent.execute_action(action)
        assert result.success is True
        assert isinstance(result.data, dict)

    @pytest.mark.asyncio
    async def test_screenshot(self, agent):
        await agent.open()
        screenshot = await agent.screenshot()
        assert isinstance(screenshot, bytes)

    @pytest.mark.asyncio
    async def test_go_back(self, agent):
        await agent.open()
        await agent.navigate("https://page1.gov.in")
        await agent.navigate("https://page2.gov.in")
        action = BrowserAction(type=BrowserActionType.GO_BACK)
        result = await agent.execute_action(action)
        assert result.success is True
        assert await agent.current_url() == "https://page1.gov.in"

    @pytest.mark.asyncio
    async def test_actions_log(self, agent):
        await agent.open()
        action1 = BrowserAction(type=BrowserActionType.NAVIGATE, url="https://example.gov.in")
        await agent.execute_action(action1)
        action2 = BrowserAction(type=BrowserActionType.CLICK)
        await agent.execute_action(action2)
        log = agent.get_actions_log()
        assert len(log) == 2

    @pytest.mark.asyncio
    async def test_set_mock_page(self, agent):
        page = PageInfo(
            url="https://test.gov.in",
            title="Test Page",
            content="Test content",
        )
        agent.set_mock_page("https://test.gov.in", page)
        await agent.navigate("https://test.gov.in")
        inspected = await agent.inspect()
        assert inspected.title == "Test Page"


class TestBrowserProviderExtensibility:
    """Test that both mock and playwright agents implement the same interface."""

    def test_mock_implements_interface(self):
        from packages.browser.interfaces.agent import BrowserAgent
        agent = MockBrowserAgent()
        assert isinstance(agent, BrowserAgent)

    def test_playwright_implements_interface(self):
        from packages.browser.interfaces.agent import BrowserAgent
        from packages.browser.playwright_agent.agent import PlaywrightBrowserAgent
        agent = PlaywrightBrowserAgent()
        assert isinstance(agent, BrowserAgent)
