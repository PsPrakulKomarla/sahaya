"""Tests for BrowserAgent interface and MockBrowserAgent."""

import pytest
from packages.browser.interfaces.agent import BrowserAgent, BrowserConfig, BrowserResult
from packages.browser.interfaces.models import (
    ElementType,
    PageModel,
    SemanticElement,
    BrowserEvent,
    BrowserEventType,
)
from packages.browser.mock_agent import MockBrowserAgent


def _make_button(text: str, visible: bool = True) -> SemanticElement:
    return SemanticElement(
        role=ElementType.BUTTON,
        text=text,
        label=text,
        visible=visible,
        enabled=True,
    )


def _make_input(label: str, input_type: str = "text") -> SemanticElement:
    return SemanticElement(
        role=ElementType.INPUT,
        label=label,
        input_type=input_type,
        placeholder=f"Enter {label}",
        visible=True,
        enabled=True,
    )


class TestBrowserAgentInterface:
    def test_browser_agent_is_abstract(self):
        with pytest.raises(TypeError):
            BrowserAgent()

    def test_mock_implements_interface(self):
        agent = MockBrowserAgent()
        assert isinstance(agent, BrowserAgent)


class TestBrowserResult:
    def test_success_result(self):
        result = BrowserResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data == {"key": "value"}

    def test_error_result(self):
        result = BrowserResult(success=False, error="Something went wrong")
        assert result.success is False
        assert result.error == "Something went wrong"


class TestBrowserConfig:
    def test_default_config(self):
        config = BrowserConfig()
        assert config.headless is True
        assert config.timeout_seconds == 60

    def test_custom_config(self):
        config = BrowserConfig(headless=False, timeout_seconds=120)
        assert config.headless is False
        assert config.timeout_seconds == 120


class TestSemanticElement:
    def test_element_creation(self):
        el = SemanticElement(
            role=ElementType.BUTTON,
            text="Submit",
            label="Submit Button",
        )
        assert el.role == ElementType.BUTTON
        assert el.text == "Submit"
        assert el.visible is True

    def test_semantic_signature(self):
        el1 = SemanticElement(role=ElementType.BUTTON, text="Start Application")
        el2 = SemanticElement(role=ElementType.BUTTON, text="Start Application")
        assert el1.semantic_signature() == el2.semantic_signature()

    def test_semantic_signature_different(self):
        el1 = SemanticElement(role=ElementType.BUTTON, text="Start Application")
        el2 = SemanticElement(role=ElementType.BUTTON, text="Submit Form")
        assert el1.semantic_signature() != el2.semantic_signature()


class TestPageModel:
    def test_page_creation(self):
        page = PageModel(url="https://example.com", title="Test Page")
        assert page.url == "https://example.com"
        assert page.title == "Test Page"

    def test_find_elements_by_role(self):
        elements = [
            _make_button("Start"),
            _make_input("Name"),
            _make_button("Submit"),
        ]
        page = PageModel(url="https://example.com", elements=elements)
        buttons = page.find_elements(role=ElementType.BUTTON)
        assert len(buttons) == 2

    def test_find_elements_by_text(self):
        elements = [
            _make_button("Start Application"),
            _make_button("Submit"),
        ]
        page = PageModel(url="https://example.com", elements=elements)
        found = page.find_elements(text="Start")
        assert len(found) == 1
        assert found[0].text == "Start Application"

    def test_find_element_single(self):
        elements = [_make_button("Click Me")]
        page = PageModel(url="https://example.com", elements=elements)
        el = page.find_element(text="Click Me")
        assert el is not None
        assert el.text == "Click Me"

    def test_find_element_not_found(self):
        page = PageModel(url="https://example.com", elements=[])
        el = page.find_element(text="Nonexistent")
        assert el is None

    def test_has_element(self):
        elements = [_make_button("Start")]
        page = PageModel(url="https://example.com", elements=elements)
        assert page.has_element(text="Start") is True
        assert page.has_element(text="Missing") is False


class TestMockBrowserAgent:
    @pytest.fixture
    def agent(self):
        return MockBrowserAgent()

    @pytest.fixture
    def agent_with_pages(self):
        agent = MockBrowserAgent()
        agent.add_page_with_elements(
            "https://example.com",
            "Home Page",
            [
                _make_button("Start Application"),
                _make_input("Name"),
            ],
            text="Welcome to the portal",
        )
        agent.add_page_with_elements(
            "https://example.com/form",
            "Application Form",
            [
                _make_input("Full Name"),
                _make_input("Address"),
                _make_button("Submit"),
            ],
            text="Fill out the form",
        )
        return agent

    @pytest.mark.asyncio
    async def test_open_and_close(self, agent):
        result = await agent.open()
        assert result.success is True
        result = await agent.close()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_navigate(self, agent_with_pages):
        result = await agent_with_pages.navigate("https://example.com")
        assert result.success is True
        assert result.page is not None
        assert result.page.title == "Home Page"

    @pytest.mark.asyncio
    async def test_current_url(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        url = await agent_with_pages.current_url()
        assert url == "https://example.com"

    @pytest.mark.asyncio
    async def test_inspect(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        page = await agent_with_pages.inspect()
        assert page.title == "Home Page"
        assert len(page.elements) > 0

    @pytest.mark.asyncio
    async def test_find_element(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        el = await agent_with_pages.find_element(text="Start Application")
        assert el is not None
        assert el.text == "Start Application"

    @pytest.mark.asyncio
    async def test_click(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        result = await agent_with_pages.click("Start Application")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_click_not_found(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        result = await agent_with_pages.click("Nonexistent Button")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_type_text(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        result = await agent_with_pages.type_text("Name", "John Doe")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_extract_text(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        text = await agent_with_pages.extract_text()
        assert "Welcome" in text

    @pytest.mark.asyncio
    async def test_get_page_title(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        title = await agent_with_pages.get_page_title()
        assert title == "Home Page"

    @pytest.mark.asyncio
    async def test_is_visible(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        assert await agent_with_pages.is_visible("Start Application") is True
        assert await agent_with_pages.is_visible("Nonexistent") is False

    @pytest.mark.asyncio
    async def test_go_back(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        await agent_with_pages.navigate("https://example.com/form")
        await agent_with_pages.go_back()
        url = await agent_with_pages.current_url()
        assert url == "https://example.com"

    @pytest.mark.asyncio
    async def test_events_recorded(self, agent_with_pages):
        await agent_with_pages.open()
        await agent_with_pages.navigate("https://example.com")
        events = agent_with_pages.events
        assert len(events) >= 2
        assert any(e.event_type == BrowserEventType.BROWSER_STARTED for e in events)
        assert any(e.event_type == BrowserEventType.PAGE_LOADED for e in events)

    @pytest.mark.asyncio
    async def test_action_log(self, agent_with_pages):
        await agent_with_pages.navigate("https://example.com")
        await agent_with_pages.click("Start Application")
        log = agent_with_pages.action_log
        assert len(log) >= 2
        assert any(a["action"] == "navigate" for a in log)
        assert any(a["action"] == "click" for a in log)

    @pytest.mark.asyncio
    async def test_context_manager(self, agent):
        async with agent:
            pass
        assert agent._is_open is False
