"""Tests for LearningPipeline, ReuseMode, PageChangeDetector, and RecoveryEngine."""

import pytest
from packages.browser.mock_agent import MockBrowserAgent
from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement
from app.services.workflow_memory.models import (
    BrowserActionType,
    ExpectedResult,
    LearnableWorkflowStep,
    TargetDescriptor,
    WorkflowDefinition,
    WorkflowSource,
    WorkflowStatus,
)
from app.services.workflow_memory.service import WorkflowMemoryService
from app.repositories.workflow import WorkflowRepository
from app.services.browser_learning.pipeline import LearningPipeline
from app.services.browser_learning.change_detector import PageChangeDetector, ChangeDetection
from app.services.browser_learning.recovery import WorkflowRecoveryEngine
from app.services.browser_learning.reuse import ReuseMode


def _make_button(text, visible=True):
    return SemanticElement(role=ElementType.BUTTON, text=text, label=text, visible=visible, enabled=True)

def _make_input(label, input_type="text"):
    return SemanticElement(role=ElementType.INPUT, label=label, input_type=input_type, placeholder=f"Enter {label}", visible=True, enabled=True)


class TestPageChangeDetector:
    def test_no_change(self):
        detector = PageChangeDetector()
        page1 = PageModel(url="https://example.com", title="Home", elements=[_make_button("Start")])
        page2 = PageModel(url="https://example.com", title="Home", elements=[_make_button("Start")])
        result = detector.detect(page1, page2)
        assert result.changed is False

    def test_url_changed(self):
        detector = PageChangeDetector()
        page1 = PageModel(url="https://example.com/page1", title="Home")
        page2 = PageModel(url="https://example.com/page2", title="Home")
        result = detector.detect(page1, page2)
        assert result.url_changed is True
        assert result.changed is True

    def test_title_changed(self):
        detector = PageChangeDetector()
        page1 = PageModel(url="https://example.com", title="Home")
        page2 = PageModel(url="https://example.com", title="Different Title")
        result = detector.detect(page1, page2)
        assert result.title_changed is True

    def test_missing_element(self):
        detector = PageChangeDetector()
        page1 = PageModel(url="https://example.com", elements=[_make_button("Start"), _make_button("Submit")])
        page2 = PageModel(url="https://example.com", elements=[_make_button("Submit")])
        result = detector.detect(page1, page2)
        assert result.changed is True
        assert len(result.missing_elements) == 1

    def test_changed_text(self):
        detector = PageChangeDetector()
        steps = [
            LearnableWorkflowStep(
                step_id="s1",
                action=BrowserActionType.CLICK,
                target=TargetDescriptor(role="button", text="Start Application"),
            )
        ]
        page = PageModel(
            url="https://example.com",
            elements=[_make_button("Begin Application")],
        )
        result = detector.detect(None, page, expected_steps=steps)
        assert result.changed is True

    def test_severity_high(self):
        d = ChangeDetection(url_changed=True)
        assert d.severity == "high"

    def test_severity_low(self):
        d = ChangeDetection(changed_text=["text changed"])
        assert d.severity == "low"

    def test_no_expected_page(self):
        detector = PageChangeDetector()
        page = PageModel(url="https://example.com")
        result = detector.detect(None, page)
        assert result.changed is True
        assert "No expected page" in result.details


class TestWorkflowRecoveryEngine:
    @pytest.fixture
    def browser(self):
        return MockBrowserAgent()

    def test_text_similarity(self, browser):
        engine = WorkflowRecoveryEngine(browser)
        score = engine._text_similarity("Start Application", "Start Application")
        assert score == 1.0

    def test_text_similarity_partial(self, browser):
        engine = WorkflowRecoveryEngine(browser)
        score = engine._text_similarity("Start Application", "Begin Application")
        assert 0.0 < score < 1.0

    def test_text_similarity_empty(self, browser):
        engine = WorkflowRecoveryEngine(browser)
        score = engine._text_similarity("", "text")
        assert score == 0.0

    def test_find_alternatives(self, browser):
        engine = WorkflowRecoveryEngine(browser)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        page = PageModel(
            url="https://example.com",
            elements=[
                _make_button("Begin Application"),
                _make_button("Submit"),
                _make_input("Name"),
            ],
        )
        candidates = engine._find_alternatives(step, page)
        assert len(candidates) > 0

    def test_semantic_similarity(self, browser):
        engine = WorkflowRecoveryEngine(browser)
        target = TargetDescriptor(role="button", text="Start Application")
        element = SemanticElement(role=ElementType.BUTTON, text="Begin Application")
        score = engine._semantic_similarity(target, element)
        assert score > 0.0

    @pytest.mark.asyncio
    async def test_attempt_recovery_success(self, browser):
        browser.add_page_with_elements(
            "https://example.com",
            "Home",
            [_make_button("Begin Application"), _make_button("Submit")],
        )
        await browser.navigate("https://example.com")
        page = await browser.inspect()

        engine = WorkflowRecoveryEngine(browser, confidence_threshold=0.3)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        workflow = WorkflowDefinition(service_id="test")
        result = await engine.attempt_recovery(step, page, workflow)
        assert result.success is True
        assert result.recovered_step is not None

    @pytest.mark.asyncio
    async def test_attempt_recovery_no_candidates(self, browser):
        browser.add_page_with_elements(
            "https://example.com",
            "Home",
            [_make_input("Name")],
        )
        await browser.navigate("https://example.com")
        page = await browser.inspect()

        engine = WorkflowRecoveryEngine(browser, confidence_threshold=0.9)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        workflow = WorkflowDefinition(service_id="test")
        result = await engine.attempt_recovery(step, page, workflow)
        assert result.needs_human is True

    @pytest.mark.asyncio
    async def test_attempt_recovery_low_confidence(self, browser):
        browser.add_page_with_elements(
            "https://example.com",
            "Home",
            [_make_button("Something Completely Different")],
        )
        await browser.navigate("https://example.com")
        page = await browser.inspect()

        engine = WorkflowRecoveryEngine(browser, confidence_threshold=0.8)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        workflow = WorkflowDefinition(service_id="test")
        result = await engine.attempt_recovery(step, page, workflow)
        assert result.needs_human is True


class TestLearningPipeline:
    @pytest.fixture
    def browser(self):
        agent = MockBrowserAgent()
        agent.add_page_with_elements(
            "https://portal.example.com",
            "Government Portal",
            [
                _make_button("Start Application"),
                _make_input("Full Name"),
                _make_button("Submit"),
            ],
            text="Welcome to Government Portal",
        )
        return agent

    @pytest.fixture
    def pipeline(self, browser):
        return LearningPipeline(browser, memory_service=None)

    @pytest.mark.asyncio
    async def test_observe_page(self, browser):
        await browser.navigate("https://portal.example.com")
        page = await browser.inspect()
        pipeline = LearningPipeline(browser, memory_service=None)
        steps = pipeline._observe_page(page, "https://portal.example.com")
        assert len(steps) > 0

    def test_infer_action_button(self, pipeline):
        element = SemanticElement(role=ElementType.BUTTON, text="Click")
        action = pipeline._infer_action(element)
        assert action == BrowserActionType.CLICK

    def test_infer_action_input(self, pipeline):
        element = SemanticElement(role=ElementType.INPUT, input_type="text")
        action = pipeline._infer_action(element)
        assert action == BrowserActionType.FILL

    def test_infer_action_select(self, pipeline):
        element = SemanticElement(role=ElementType.SELECT)
        action = pipeline._infer_action(element)
        assert action == BrowserActionType.SELECT

    def test_validate_workflow_valid(self, pipeline):
        wf = WorkflowDefinition(
            service_id="test",
            steps=[
                LearnableWorkflowStep(
                    step_id="s1",
                    action=BrowserActionType.CLICK,
                    target=TargetDescriptor(role="button", text="Start"),
                    confidence=0.8,
                )
            ],
        )
        assert pipeline._validate_workflow(wf) is True

    def test_validate_workflow_no_steps(self, pipeline):
        wf = WorkflowDefinition(service_id="test", steps=[])
        assert pipeline._validate_workflow(wf) is False


class TestReuseMode:
    @pytest.fixture
    def browser(self):
        agent = MockBrowserAgent()
        agent.add_page_with_elements(
            "https://portal.example.com",
            "Government Portal",
            [
                _make_button("Start Application"),
                _make_input("Full Name"),
                _make_button("Submit"),
            ],
        )
        return agent

    @pytest.mark.asyncio
    async def test_perform_action_click(self, browser):
        await browser.navigate("https://portal.example.com")
        reuse = ReuseMode(browser, memory_service=None)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        result = await reuse._perform_action(step)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_perform_action_type(self, browser):
        await browser.navigate("https://portal.example.com")
        reuse = ReuseMode(browser, memory_service=None)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.FILL,
            target=TargetDescriptor(role="input", text="Full Name"),
            input_value="John Doe",
        )
        result = await reuse._perform_action(step)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_verify_step_found(self, browser):
        await browser.navigate("https://portal.example.com")
        page = await browser.inspect()
        reuse = ReuseMode(browser, memory_service=None)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Start Application"),
        )
        result = await reuse._verify_step(step, page)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_verify_step_not_found(self, browser):
        await browser.navigate("https://portal.example.com")
        page = await browser.inspect()
        reuse = ReuseMode(browser, memory_service=None)
        step = LearnableWorkflowStep(
            step_id="s1",
            action=BrowserActionType.CLICK,
            target=TargetDescriptor(role="button", text="Nonexistent"),
        )
        result = await reuse._verify_step(step, page)
        assert result.success is False
