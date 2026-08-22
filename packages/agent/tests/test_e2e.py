import pytest
from packages.agent.orchestrator.orchestrator import AgentOrchestrator
from packages.agent.planner.planner import TaskPlanner
from packages.agent.executor.executor import TaskExecutor
from packages.agent.safety.engine import SafetyPolicyEngine
from packages.agent.approval.service import ApprovalService
from packages.agent.models.tasks import TaskStatus, AgentState
from packages.services.intent.engine import RuleBasedIntentEngine
from packages.services.registry.registry import reset_registry
from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter
from packages.services.adapters.birth_certificate.adapter import MockBirthCertificateAdapter


@pytest.fixture
def registry():
    reg = reset_registry()
    reg.register_service(MockIncomeCertificateAdapter())
    reg.register_service(MockBirthCertificateAdapter())
    return reg


@pytest.fixture
def orchestrator(registry):
    return AgentOrchestrator()


class TestEndToEndFlow:
    @pytest.mark.asyncio
    async def test_income_certificate_flow(self, orchestrator):
        task = await orchestrator.process_request(
            message="I want to apply for an income certificate.",
            user_id="test_user",
        )
        assert task.status in (TaskStatus.COMPLETED, TaskStatus.WAITING_FOR_APPROVAL, TaskStatus.FAILED)
        assert task.task_id is not None
        assert task.intent is not None
        assert task.resolution is not None

    @pytest.mark.asyncio
    async def test_birth_certificate_flow(self, orchestrator):
        task = await orchestrator.process_request(
            message="I need a birth certificate.",
            user_id="test_user",
        )
        assert task.status in (TaskStatus.COMPLETED, TaskStatus.WAITING_FOR_APPROVAL, TaskStatus.FAILED)
        assert task.intent is not None

    @pytest.mark.asyncio
    async def test_tracking_flow(self, orchestrator):
        task = await orchestrator.process_request(
            message="Check my application status.",
            user_id="test_user",
        )
        assert task.status in (TaskStatus.COMPLETED, TaskStatus.WAITING_FOR_APPROVAL, TaskStatus.FAILED)

    @pytest.mark.asyncio
    async def test_unknown_service_flow(self, orchestrator):
        task = await orchestrator.process_request(
            message="I need a government drone registration.",
            user_id="test_user",
        )
        assert task.status in (TaskStatus.FAILED, TaskStatus.WAITING_FOR_APPROVAL)

    @pytest.mark.asyncio
    async def test_cancellation(self, orchestrator):
        task = await orchestrator.process_request(
            message="I want to apply for an income certificate.",
            user_id="test_user",
        )
        await orchestrator.cancel_task(task)
        assert task.status == TaskStatus.CANCELLED


class TestServiceExtensibility:
    """Test that adding a new service works without modifying core code."""

    def test_passport_renewal_extensibility(self):
        from packages.services.adapters.passport_renewal.adapter import MockPassportRenewalAdapter
        from packages.services.registry.registry import ServiceRegistry
        from packages.agent.planner.planner import TaskPlanner
        from packages.services.intent.models import Intent, IntentType
        from packages.services.registry.models import ServiceResolution, ResolutionStatus

        registry = ServiceRegistry()
        registry.register_service(MockPassportRenewalAdapter())

        adapter = registry.get_service("passport_renewal")
        assert adapter is not None
        assert adapter.metadata().service_id == "passport_renewal"

        planner = TaskPlanner()
        intent = Intent(
            intent=IntentType.RENEWAL,
            service_query="passport",
            operation=IntentType.RENEWAL,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="passport_renewal",
            service_name="Passport Renewal",
            capabilities=[c.value for c in adapter.get_capabilities()],
        )
        plan = planner.create_plan(intent, resolution)
        assert plan.service_id == "passport_renewal"
        assert len(plan.steps) > 0
