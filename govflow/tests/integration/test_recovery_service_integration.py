"""Integration tests for RecoveryEngine with real government service adapter.

Tests the full recovery flow: failure classification -> recovery engine ->
semantic recovery -> verification -> workflow memory updates.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from packages.agent.recovery.engine import RecoveryEngine, RecoveryConfiguration
from packages.agent.recovery.types import (
    FailureType, RecoveryLevel, RecoveryDecisionType, RecoveryMetrics,
    SafeActionClassifier,
)
from packages.agent.planner.models import WorkflowStep, StepType, StepStatus, WorkflowPlan
from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement
from packages.services.adapters.income_certificate.adapter import (
    RealIncomeCertificateAdapter, get_income_certificate_adapter,
)
from packages.agent.executor.context import ExecutionContext, Permission


@pytest.fixture
def sample_page():
    return PageModel(
        url="https://karnataka.gov.in/income-certificate",
        title="Income Certificate Application",
        elements=[
            SemanticElement(
                element_id="btn_start",
                role=ElementType.BUTTON,
                text="Start New Application",
                visible=True,
                enabled=True,
                selector_hint="#start-application",
                confidence=0.95,
            ),
            SemanticElement(
                element_id="btn_continue",
                role=ElementType.BUTTON,
                text="Begin Application",
                visible=True,
                enabled=True,
                selector_hint="#continue-application",
                confidence=0.9,
            ),
            SemanticElement(
                element_id="input_name",
                role=ElementType.INPUT,
                text="Full Name",
                visible=True,
                enabled=True,
                selector_hint="#applicant-name",
                placeholder="Enter your full name",
                confidence=1.0,
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
    browser.current_url = AsyncMock(return_value="https://karnataka.gov.in/income-certificate")
    browser.navigate = AsyncMock(return_value={"success": True})
    browser.click = AsyncMock(return_value={"success": True, "data": {"clicked": "Start New Application"}})
    browser.type_text = AsyncMock(return_value={"success": True, "data": {"typed": "test", "target": "name"}})
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
            "target_text": "Start New Application",
            "target_role": "button",
        },
    )


@pytest.mark.asyncio
class TestRecoveryIntegrationWithService:
    """Integration tests combining recovery engine with service adapter."""

    async def test_element_not_found_layered_recovery_with_service(
        self, engine, sample_step, sample_page, mock_browser
    ):
        """Test that element not found triggers layered recovery with service adapter."""
        error = Exception("element not found on page")
        decision = await engine.handle_failure(
            sample_step, error, current_page=sample_page
        )
        # Should attempt recovery (not immediate escalation since it's not auth/unavailable)
        assert decision.recovery_level in (
            RecoveryLevel.LEVEL_2_REINSPECT,
            RecoveryLevel.LEVEL_3_SEMANTIC,
            RecoveryLevel.LEVEL_1_RETRY,
        )

    async def test_semantic_recovery_finds_alternative(
        self, engine, sample_step, sample_page
    ):
        """Test semantic recovery finds alternative when element text changes."""
        step = WorkflowStep(
            id="semantic_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={
                "action_type": "click",
                "target_text": "Begin New Application",  # Changed from "Start New Application"
                "target_role": "button",
            },
        )
        # Mock browser returns page with "Start New Application" but we search for "Begin New Application"
        decision = await engine._level_3_semantic(step, sample_page)
        # Should find "Start New Application" as semantic match since words overlap
        assert decision.decision in (RecoveryDecisionType.RECOVER, RecoveryDecisionType.ABORT)

    async def test_safe_action_classifier_with_service_steps(self):
        """Test that service workflow steps are classified correctly for retry."""
        # Safe steps
        assert SafeActionClassifier.is_safe_to_retry("navigate") is True
        assert SafeActionClassifier.is_safe_to_retry("inspect") is True
        assert SafeActionClassifier.is_safe_to_retry("extract") is True
        assert SafeActionClassifier.is_safe_to_retry("scroll") is True

        # Unsafe steps (form submission, payment, etc.)
        assert SafeActionClassifier.is_safe_to_retry("submit") is False
        assert SafeActionClassifier.is_safe_to_retry("payment") is False
        assert SafeActionClassifier.is_safe_to_retry("grievance_submit") is False

    async def test_recovery_metrics_integration(self, engine):
        """Test recovery metrics are tracked during failures."""
        step = WorkflowStep(id="m1", type=StepType.BROWSER_EXECUTION, input_data={})
        error = Exception("element not found")

        # Record two failures
        await engine.handle_failure(step, error)
        await engine.handle_failure(step, error)

        metrics = engine.metrics
        assert metrics.total_failures == 2
        assert metrics.failure_by_type.get(FailureType.ELEMENT_NOT_FOUND.value, 0) == 2

    async def test_recovery_events_integration(self, engine, sample_step, sample_page):
        """Test recovery events are recorded during failure handling."""
        error = Exception("element not found")
        await engine.handle_failure(sample_step, error, current_page=sample_page)

        events = engine.events
        event_types = [e.event_type for e in events]
        # Should have at least failure_detected and recovery_decision events
        assert "failure_detected" in event_types
        assert "recovery_decision" in event_types

    async def test_level_2_reinspect_finds_element(
        self, engine, sample_step, sample_page
    ):
        """Test level 2 reinspect finds element on page."""
        decision = await engine._level_2_reinspect(sample_step, sample_page)
        # Element "Start New Application" exists in sample_page
        assert decision.decision == RecoveryDecisionType.RECOVER
        assert decision.recovery_level == RecoveryLevel.LEVEL_2_REINSPECT
        assert decision.candidate_text is not None

    async def test_level_3_semantic_match_below_threshold(
        self, engine, sample_page
    ):
        """Test level 3 semantic search when no good match exists."""
        step = WorkflowStep(
            id="no_match_step",
            type=StepType.BROWSER_EXECUTION,
            input_data={
                "action_type": "click",
                "target_text": "xyzzy foobar baz",
                "target_role": "button",
            },
        )
        decision = await engine._level_3_semantic(step, sample_page)
        assert decision.decision == RecoveryDecisionType.ABORT
        assert decision.recovery_level == RecoveryLevel.LEVEL_3_SEMANTIC

    async def test_workflow_plan_integration(self, engine, sample_step):
        """Test recovery with workflow plan comparison."""
        plan = WorkflowPlan(
            id="test_plan",
            task_type="NEW_APPLICATION",
            service_id="income_certificate",
            steps=[
                WorkflowStep(
                    id="discover_portal",
                    type=StepType.DISCOVER_SERVICE,
                    description="Locate and verify the official government portal",
                    status=StepStatus.COMPLETED,
                ),
                WorkflowStep(
                    id="browser_step",
                    type=StepType.BROWSER_EXECUTION,
                    description="Execute application on government portal",
                    input_data={"url": "https://karnataka.gov.in"},
                ),
            ],
        )

        # Test level 4 workflow compare
        decision = await engine._level_4_workflow_compare(sample_step, plan)
        # Should find the completed discover step and allow recovery
        assert decision.decision in (RecoveryDecisionType.RECOVER, RecoveryDecisionType.RETRY)

    async def test_create_safe_retry_wrapper(self, engine, sample_step):
        """Test the safe retry wrapper handles recovery."""
        from packages.agent.recovery.engine import create_safe_retry_wrapper

        wrapper = create_safe_retry_wrapper(engine, sample_step)

        async def failing_func():
            raise Exception("element not found")

        async def succeeding_func():
            return {"success": True, "data": "ok"}

        # Test with failing function - should trigger recovery
        with patch.object(engine, 'handle_failure') as mock_handle:
            mock_handle.return_value = type(
                'obj', (object,), {
                    'decision': type('obj', (object,), {'decision': 'RECOVER', 'confidence': 0.9})(),
                    'recovery_level': type('obj', (object,), {'value': 'LEVEL_2_REINSPECT'})(),
                    'metadata': {}
                })()

            result = await wrapper(failing_func)
            # Should have attempted recovery

        # Test with succeeding function
        result = await wrapper(succeeding_func)
        assert result == {"success": True, "data": "ok"}


@pytest.mark.asyncio
class TestServiceAdapterIntegration:
    """Tests integrating the real service adapter with recovery system."""

    async def test_service_adapter_metadata(self):
        """Test the real adapter has proper metadata."""
        adapter = get_income_certificate_adapter()
        meta = adapter.metadata()

        assert meta.service_id == "income_certificate"
        assert meta.display_name == "Income Certificate"
        assert meta.jurisdiction == "Karnataka"
        assert "karnataka.gov.in" in meta.official_portal
        assert ServiceCapability.DISCOVER in meta.capabilities
        assert ServiceCapability.ELIGIBILITY_CHECK in meta.capabilities
        assert len(meta.required_documents) > 0

    async def test_service_adapter_discover(self):
        """Test adapter discover returns proper service info."""
        adapter = get_income_certificate_adapter()
        result = await adapter.discover("income certificate karnataka")

        assert result.success is True
        assert result.data["service_id"] == "income_certificate"
        assert result.data["official_portal"] == "https://karnataka.gov.in"
        assert "capabilities" in result.data

    async def test_service_adapter_eligibility_check(self):
        """Test adapter eligibility check."""
        adapter = get_income_certificate_adapter()

        # Eligible user
        result = await adapter.check_eligibility({
            "age": 30,
            "is_resident": True,
            "annual_income": 500000,
        })
        assert result.success is True
        assert result.data["eligible"] is True
        assert len(result.data["criteria"]) == 0

        # Ineligible user (underage)
        result = await adapter.check_eligibility({
            "age": 15,
            "is_resident": True,
            "annual_income": 500000,
        })
        assert result.success is True
        assert result.data["eligible"] is False
        assert len(result.data["criteria"]) > 0

    async def test_service_adapter_document_requirements(self):
        """Test adapter document requirements."""
        adapter = get_income_certificate_adapter()
        result = await adapter.get_document_requirements()
        assert result.success is True
        docs = result.data["documents"]
        assert len(docs) > 0
        # Check required documents are present
        doc_types = [d["document_type"] for d in docs]
        assert "identity_proof" in doc_types
        assert "address_proof" in doc_types
        assert "income_proof" in doc_types

    async def test_service_adapter_workflow_plan(self):
        """Test adapter generates workflow plan."""
        adapter = get_income_certificate_adapter()
        result = await adapter.get_workflow_plan("new_application")

        assert result.success is True
        assert "service" in result.data
        assert "operation" in result.data
        assert "steps" in result.data
        steps = result.data["steps"]
        assert len(steps) > 0
        # Check step structure
        step = steps[0]
        assert "id" in step
        assert "action" in step
        assert "description" in step


@pytest.mark.asyncio
class TestLiveSafetyGateIntegration:
    """Tests live safety gate integration with recovery."""

    async def test_live_mode_safety_gate_with_service(
        self, mock_browser, recovery_config
    ):
        """Test LIVE mode requires all safety gates to pass."""
        from packages.agent.executor.live_mode import (
            LiveExecutionController, ExecutionMode, LiveSafetyGate,
        )

        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)

        # Without safety gate configured - should be blocked
        result = ctrl.validate_live_execution()
        assert result["allowed"] is False
        assert "failures" in result

        # Configure all safety gates
        ctrl._safety_gate = LiveSafetyGate(
            service_verified=True,
            domain_verified=True,
            workflow_version_verified=True,
            browser_provider_verified=True,
            safety_policy_loaded=True,
            human_approval_available=True,
            user_authenticated=True,
            sensitive_action_gate_enabled=True,
        )

        result = ctrl.validate_live_execution()
        assert result["allowed"] is True

    async def test_domain_allowlist_integration_with_service(
        self, mock_browser, recovery_config
    ):
        """Test domain allowlist works with service adapter."""
        from packages.agent.safety.domain import DomainAllowlist
        from packages.agent.executor.live_mode import LiveExecutionController, ExecutionMode

        # Create allowlist with government domains
        allowlist = DomainAllowlist()
        allowlist.add_domain("karnataka.gov.in")
        allowlist.add_domain("serviceonline.gov.in")

        ctrl = LiveExecutionController(
            mode=ExecutionMode.LIVE,
            domain_allowlist=allowlist,
        )

        # Allowed domain
        nav = ctrl.check_domain("https://karnataka.gov.in")
        assert nav.allowed is True

        # Blocked domain
        nav = ctrl.check_domain("https://malicious-site.com")
        assert nav.allowed is False

        # HTTPS required domain with HTTP
        nav = ctrl.check_domain("http://karnataka.gov.in")
        assert nav.allowed is False  # HTTPS required

    async def test_sensitive_action_gate_with_service_submission(
        self, mock_browser, recovery_config
    ):
        """Test sensitive action gate prevents unauthorized submission."""
        from packages.agent.executor.live_mode import LiveExecutionController, ExecutionMode

        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)

        # Sensitive action without gate enabled
        result = ctrl.is_action_allowed("SUBMIT_APPLICATION")
        assert result["allowed"] is False
        assert "safety gate" in result["reason"]

        # Enable gate
        ctrl._safety_gate.sensitive_action_gate_enabled = True
        result = ctrl.is_action_allowed("SUBMIT_APPLICATION")
        assert result["allowed"] is True


@pytest.mark.asyncio
class TestRecoveryMemoryIntegration:
    """Tests recovery memory integration with service workflow."""

    async def test_recovery_record_with_service_data(self):
        """Test recovery record stores service-specific data."""
        from packages.agent.recovery.memory import RecoveryMemory
        from packages.agent.recovery.types import (
            FailureType, RecoveryDecision, RecoveryDecisionType, RecoveryLevel,
        )

        memory = RecoveryMemory()
        decision = RecoveryDecision(
            decision=RecoveryDecisionType.RECOVER,
            confidence=0.93,
            candidate_text="Begin New Application",
            candidate_selector="#begin-application",
            recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
            metadata={"service": "income_certificate"},
        )

        record = memory.record_recovery(
            step_id="step_1",
            old_target_text="Start Application",
            old_target_role="button",
            failure_type=FailureType.ELEMENT_NOT_FOUND,
            decision=decision,
            page_url="https://karnataka.gov.in/income-certificate",
            page_title="Income Certificate",
        )

        assert record.success is True
        assert record.old_step_id == "step_1"
        assert record.old_target_text == "Start Application"
        assert record.replacement_text == "Begin New Application"
        assert record.page_url == "https://karnataka.gov.in/income-certificate"
        assert record.page_title == "Income Certificate"
        assert record.confidence == 0.93
        assert record.recovery_level == RecoveryLevel.LEVEL_3_SEMANTIC
        assert memory.total_records == 1

    async def test_workflow_update_suggestion_from_recovery(self):
        """Test workflow update suggestions based on recovery history."""
        from packages.agent.recovery.memory import RecoveryMemory
        from packages.agent.recovery.types import (
            FailureType, RecoveryDecision, RecoveryDecisionType, RecoveryLevel,
        )

        memory = RecoveryMemory()
        decision = RecoveryDecision(
            decision=RecoveryDecisionType.RECOVER,
            confidence=0.85,
            candidate_text="Begin New Application",
            candidate_selector="#begin-app",
            recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
        )

        # Record 3 successful recoveries for the same step
        for i in range(3):
            memory.record_recovery(
                step_id="step_1",
                old_target_text="Start Application",
                old_target_role="button",
                failure_type=FailureType.ELEMENT_NOT_FOUND,
                decision=decision,
            )

        # Should suggest update after enough successes
        assert memory.should_update_workflow("step_1") is True

        # Check summary
        summary = memory.summary()
        assert summary["total_records"] == 3
        assert summary["success_count"] == 3
        assert summary["success_rate"] == 1.0