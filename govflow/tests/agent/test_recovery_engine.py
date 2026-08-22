"""Tests for RecoveryEngine — layered recovery for browser agent failures."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from packages.agent.recovery.engine import RecoveryEngine, RecoveryConfiguration
from packages.agent.recovery.types import (
    FailureType,
    RecoveryLevel,
    RecoveryDecisionType,
    RecoveryMetrics,
    SafeActionClassifier,
)
from packages.agent.planner.models import WorkflowStep, StepType, StepStatus, WorkflowPlan
from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement


@pytest.fixture
def sample_page():
    return PageModel(
        url="https://example.com/form",
        title="Application Form",
        elements=[
            SemanticElement(
                element_id="btn_submit",
                role=ElementType.BUTTON,
                text="Submit Application",
                visible=True,
                enabled=True,
                selector_hint="#btn-submit",
                confidence=0.95,
            ),
            SemanticElement(
                element_id="input_name",
                role=ElementType.INPUT,
                text="Full Name",
                visible=True,
                enabled=True,
                selector_hint="#input-name",
                placeholder="Enter your full name",
                confidence=1.0,
            ),
            SemanticElement(
                element_id="btn_cancel",
                role=ElementType.BUTTON,
                text="Cancel",
                visible=True,
                enabled=True,
                selector_hint="#btn-cancel",
                confidence=0.9,
            ),
        ],
    )


@pytest.fixture
def recovery_config():
    return RecoveryConfiguration(
        max_step_recovery_attempts=2,
        max_workflow_recovery_attempts=3,
        retry_delay_seconds=0.01,
    )


@pytest_asyncio.fixture
async def mock_browser(sample_page):
    browser = AsyncMock()
    browser.inspect = AsyncMock(return_value=sample_page)
    browser.current_url = AsyncMock(return_value="https://example.com/form")
    return browser


@pytest_asyncio.fixture
async def engine(mock_browser, recovery_config):
    return RecoveryEngine(browser=mock_browser, config=recovery_config)


@pytest.fixture
def sample_step():
    return WorkflowStep(
        id="test_step",
        type=StepType.BROWSER_EXECUTION,
        description="Click submit button",
        input_data={
            "action_type": "click",
            "target_text": "Submit Application",
            "target_role": "button",
        },
    )


class TestRecoveryEngine:
    @pytest.mark.asyncio
    async def test_failure_classification_session_expired(self, engine):
        error = Exception("session has expired")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.recovery_level == RecoveryLevel.LEVEL_6_ASK_USER

    @pytest.mark.asyncio
    async def test_failure_classification_authentication(self, engine):
        error = Exception("authentication required to access page")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.recovery_level == RecoveryLevel.LEVEL_6_ASK_USER

    @pytest.mark.asyncio
    async def test_failure_classification_website_unavailable(self, engine):
        error = Exception("service unavailable 503")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.recovery_level == RecoveryLevel.LEVEL_6_ASK_USER

    @pytest.mark.asyncio
    async def test_failure_classification_element_not_found(self, engine):
        error = Exception("element not found on page")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision in (
            RecoveryDecisionType.RECOVER,
            RecoveryDecisionType.RETRY,
            RecoveryDecisionType.ABORT,
        )

    @pytest.mark.asyncio
    async def test_failure_classification_timeout(self, engine):
        error = Exception("timeout waiting for element")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision in (
            RecoveryDecisionType.RECOVER,
            RecoveryDecisionType.RETRY,
            RecoveryDecisionType.ABORT,
        )

    @pytest.mark.asyncio
    async def test_failure_classification_stale_element(self, engine):
        error = Exception("stale element reference")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision in (
            RecoveryDecisionType.RECOVER,
            RecoveryDecisionType.RETRY,
            RecoveryDecisionType.ABORT,
        )

    @pytest.mark.asyncio
    async def test_failure_classification_unknown(self, engine):
        error = Exception("something weird happened")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision in (
            RecoveryDecisionType.RECOVER,
            RecoveryDecisionType.RETRY,
            RecoveryDecisionType.ABORT,
        )

    @pytest.mark.asyncio
    async def test_session_expired_immediate_escalation(self, engine):
        error = Exception("session timed out")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.confidence == 1.0

    @pytest.mark.asyncio
    async def test_authentication_required_immediate_escalation(self, engine):
        error = Exception("login required")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.confidence == 1.0

    @pytest.mark.asyncio
    async def test_website_unavailable_immediate_escalation(self, engine):
        error = Exception("connection refused to server")
        step = WorkflowStep(id="s1", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.confidence == 1.0

    @pytest.mark.asyncio
    async def test_element_not_found_layered_recovery(self, engine, sample_step, sample_page):
        error = Exception("element not found")
        decision = await engine.handle_failure(sample_step, error, current_page=sample_page)
        assert decision.decision in (
            RecoveryDecisionType.RECOVER,
            RecoveryDecisionType.RETRY,
            RecoveryDecisionType.ABORT,
        )
        assert decision.recovery_level in (
            RecoveryLevel.LEVEL_2_REINSPECT,
            RecoveryLevel.LEVEL_3_SEMANTIC,
            RecoveryLevel.LEVEL_1_RETRY,
            RecoveryLevel.LEVEL_7_FAIL,
        )

    @pytest.mark.asyncio
    async def test_step_recovery_attempt_limit_exceeded(self, engine):
        step = WorkflowStep(id="limited_step", type=StepType.BROWSER_EXECUTION, input_data={})
        error = Exception("element not found")
        for _ in range(engine._config.max_step_recovery_attempts):
            await engine.handle_failure(step, error)
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ASK_USER
        assert decision.reason == "max_step_recovery_attempts_exceeded"

    @pytest.mark.asyncio
    async def test_workflow_recovery_attempt_limit_exceeded(self, engine):
        step = WorkflowStep(id="wf_step", type=StepType.BROWSER_EXECUTION, input_data={})
        error = Exception("element not found")
        for _ in range(engine._config.max_workflow_recovery_attempts):
            await engine.handle_failure(step, error)
            engine.reset_step_attempts(step.id)
        decision = await engine.handle_failure(step, error)
        assert decision.decision == RecoveryDecisionType.ABORT
        assert decision.reason == "max_workflow_recovery_attempts_exceeded"

    @pytest.mark.asyncio
    async def test_level_1_retry_safe_action(self, engine):
        step = WorkflowStep(
            id="safe_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={"action_type": "navigate"},
        )
        decision = await engine._level_1_retry(step)
        assert decision.decision == RecoveryDecisionType.RETRY
        assert decision.recovery_level == RecoveryLevel.LEVEL_1_RETRY

    @pytest.mark.asyncio
    async def test_level_1_retry_unsafe_action(self, engine):
        step = WorkflowStep(
            id="unsafe_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={"action_type": "submit"},
        )
        decision = await engine._level_1_retry(step)
        assert decision.decision == RecoveryDecisionType.ABORT
        assert decision.recovery_level == RecoveryLevel.LEVEL_1_RETRY

    @pytest.mark.asyncio
    async def test_level_2_reinspect_element_found(self, engine, sample_step, sample_page):
        decision = await engine._level_2_reinspect(sample_step, sample_page)
        assert decision.decision == RecoveryDecisionType.RECOVER
        assert decision.recovery_level == RecoveryLevel.LEVEL_2_REINSPECT
        assert decision.candidate_text is not None

    @pytest.mark.asyncio
    async def test_level_2_reinspect_element_not_found(self, engine, sample_page):
        step = WorkflowStep(
            id="missing_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={"target_text": "Nonexistent Widget", "target_role": "button"},
        )
        decision = await engine._level_2_reinspect(step, sample_page)
        assert decision.decision == RecoveryDecisionType.ABORT
        assert decision.recovery_level == RecoveryLevel.LEVEL_2_REINSPECT

    @pytest.mark.asyncio
    async def test_level_3_semantic_match_found(self, engine, sample_page):
        step = WorkflowStep(
            id="semantic_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={"target_text": "Submit Application", "target_role": "button"},
        )
        decision = await engine._level_3_semantic(step, sample_page)
        assert decision.decision == RecoveryDecisionType.RECOVER
        assert decision.recovery_level == RecoveryLevel.LEVEL_3_SEMANTIC
        assert decision.confidence >= engine._config.confidence_threshold

    @pytest.mark.asyncio
    async def test_level_3_semantic_below_threshold(self, engine, sample_page):
        step = WorkflowStep(
            id="no_match_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={"target_text": "xyzzy foobar baz", "target_role": "button"},
        )
        decision = await engine._level_3_semantic(step, sample_page)
        assert decision.decision == RecoveryDecisionType.ABORT
        assert decision.recovery_level == RecoveryLevel.LEVEL_3_SEMANTIC

    @pytest.mark.asyncio
    async def test_recovery_metrics_tracking(self, engine):
        step = WorkflowStep(id="m1", type=StepType.BROWSER_EXECUTION, input_data={})
        error = Exception("element not found")
        await engine.handle_failure(step, error)
        await engine.handle_failure(step, error)
        metrics = engine.metrics
        assert metrics.total_failures == 2
        assert metrics.failure_by_type.get(FailureType.ELEMENT_NOT_FOUND.value, 0) == 2

    @pytest.mark.asyncio
    async def test_recovery_events_recorded(self, engine):
        step = WorkflowStep(id="e1", type=StepType.BROWSER_EXECUTION, input_data={})
        error = Exception("element not found")
        await engine.handle_failure(step, error)
        events = engine.events
        assert len(events) >= 2
        event_types = [e.event_type for e in events]
        assert "failure_detected" in event_types
        assert "recovery_decision" in event_types

    @pytest.mark.asyncio
    async def test_attempt_recovery_delegates_to_handle_failure(self, engine):
        step = WorkflowStep(id="ar1", type=StepType.BROWSER_EXECUTION, input_data={})
        error = Exception("timeout")
        decision = await engine.attempt_recovery(step, error=error)
        assert isinstance(decision.decision, RecoveryDecisionType)

    @pytest.mark.asyncio
    async def test_attempt_recovery_default_error(self, engine):
        step = WorkflowStep(id="ar2", type=StepType.BROWSER_EXECUTION, input_data={})
        decision = await engine.attempt_recovery(step)
        assert isinstance(decision.decision, RecoveryDecisionType)


class TestSafeActionClassifier:
    def test_navigate_is_safe(self):
        assert SafeActionClassifier.is_safe_to_retry("navigate") is True

    def test_inspect_is_safe(self):
        assert SafeActionClassifier.is_safe_to_retry("inspect") is True

    def test_extract_is_safe(self):
        assert SafeActionClassifier.is_safe_to_retry("extract") is True

    def test_scroll_is_safe(self):
        assert SafeActionClassifier.is_safe_to_retry("scroll") is True

    def test_submit_is_unsafe(self):
        assert SafeActionClassifier.is_safe_to_retry("submit") is False

    def test_payment_is_unsafe(self):
        assert SafeActionClassifier.is_safe_to_retry("payment") is False

    def test_grievance_submit_is_unsafe(self):
        assert SafeActionClassifier.is_safe_to_retry("grievance_submit") is False

    def test_delete_is_unsafe(self):
        assert SafeActionClassifier.is_safe_to_retry("delete") is False

    def test_unknown_action_is_unsafe(self):
        assert SafeActionClassifier.is_safe_to_retry("unknown_action") is False

    def test_requires_idempotency_check_submit(self):
        assert SafeActionClassifier.requires_idempotency_check("submit") is True

    def test_requires_idempotency_check_navigate(self):
        assert SafeActionClassifier.requires_idempotency_check("navigate") is False

    def test_normalization_with_hyphen(self):
        assert SafeActionClassifier.is_safe_to_retry("go-back") is True

    def test_normalization_unsafe(self):
        assert SafeActionClassifier.is_safe_to_retry("final-confirmation") is False


class TestRecoveryMetrics:
    def test_record_failure(self):
        metrics = RecoveryMetrics()
        metrics.record_failure(FailureType.ELEMENT_NOT_FOUND)
        assert metrics.total_failures == 1
        assert metrics.failure_by_type[FailureType.ELEMENT_NOT_FOUND.value] == 1

    def test_record_multiple_failures(self):
        metrics = RecoveryMetrics()
        metrics.record_failure(FailureType.ELEMENT_NOT_FOUND)
        metrics.record_failure(FailureType.ELEMENT_NOT_FOUND)
        metrics.record_failure(FailureType.TIMEOUT)
        assert metrics.total_failures == 3
        assert metrics.failure_by_type[FailureType.ELEMENT_NOT_FOUND.value] == 2
        assert metrics.failure_by_type[FailureType.TIMEOUT.value] == 1

    def test_record_recovery_attempt_success(self):
        metrics = RecoveryMetrics()
        metrics.record_recovery_attempt(RecoveryLevel.LEVEL_1_RETRY, success=True)
        assert metrics.total_recovery_attempts == 1
        assert metrics.successful_recoveries == 1
        assert metrics.failed_recoveries == 0

    def test_record_recovery_attempt_failure(self):
        metrics = RecoveryMetrics()
        metrics.record_recovery_attempt(RecoveryLevel.LEVEL_2_REINSPECT, success=False)
        assert metrics.total_recovery_attempts == 1
        assert metrics.successful_recoveries == 0
        assert metrics.failed_recoveries == 1

    def test_recovery_rate(self):
        metrics = RecoveryMetrics()
        metrics.total_failures = 10
        metrics.total_recovery_attempts = 4
        assert metrics.recovery_rate == 0.4

    def test_recovery_rate_zero_failures(self):
        metrics = RecoveryMetrics()
        assert metrics.recovery_rate == 0.0

    def test_recovery_success_rate(self):
        metrics = RecoveryMetrics()
        metrics.total_recovery_attempts = 10
        metrics.successful_recoveries = 7
        assert metrics.recovery_success_rate == 0.7

    def test_recovery_success_rate_zero_attempts(self):
        metrics = RecoveryMetrics()
        assert metrics.recovery_success_rate == 0.0

    def test_user_escalation_rate(self):
        metrics = RecoveryMetrics()
        metrics.total_failures = 20
        metrics.user_escalations = 5
        assert metrics.user_escalation_rate == 0.25

    def test_user_escalation_rate_zero_failures(self):
        metrics = RecoveryMetrics()
        assert metrics.user_escalation_rate == 0.0

    def test_record_user_escalation(self):
        metrics = RecoveryMetrics()
        metrics.record_user_escalation()
        metrics.record_user_escalation()
        assert metrics.user_escalations == 2

    def test_record_workflow_update(self):
        metrics = RecoveryMetrics()
        metrics.record_workflow_update()
        assert metrics.workflow_updates == 1
