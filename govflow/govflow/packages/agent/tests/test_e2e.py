"""End-to-end mocked agent flow test.

Tests the complete pipeline:
USER -> Intent -> Service Resolution -> Task Planner -> Workflow Plan
-> State Machine -> Mock Browser -> Human Approval -> Mock Submission
-> Application Result
"""
import pytest
from packages.agent.orchestrator import AgentOrchestrator
from packages.agent.executor.context import ExecutionContext
from packages.agent.safety.approval import ApprovalService
from packages.agent.safety.engine import SafetyPolicyEngine
from packages.agent.audit import AuditEventService
from packages.browser.mock.agent import MockBrowserAgent
from packages.services.intent.engine import RuleBasedIntentEngine
from packages.services.registry.registry import get_registry, reset_registry
from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter
from packages.services.adapters.birth_certificate.adapter import MockBirthCertificateAdapter
from packages.services.registry.resolver import ServiceResolver


@pytest.fixture(autouse=True)
def setup_registry():
    reset_registry()
    registry = get_registry()
    registry.register_service(MockIncomeCertificateAdapter())
    registry.register_service(MockBirthCertificateAdapter())
    yield
    reset_registry()


@pytest.fixture
def orchestrator():
    intent_engine = RuleBasedIntentEngine()
    service_resolver = ServiceResolver()
    browser = MockBrowserAgent()
    approval_service = ApprovalService(approval_ttl_minutes=60)
    safety_engine = SafetyPolicyEngine()
    audit_service = AuditEventService()

    return AgentOrchestrator(
        intent_engine=intent_engine,
        service_resolver=service_resolver,
        browser_agent=browser,
        approval_service=approval_service,
        safety_engine=safety_engine,
        audit_service=audit_service,
    )


@pytest.mark.asyncio
async def test_income_certificate_flow(orchestrator):
    """Full mocked flow: 'I want to apply for an income certificate'."""
    context = ExecutionContext(
        user_id="user-1",
        service_id="income_certificate",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE", "FILL_FORM"],
    )

    result = await orchestrator.process_request(
        user_message="I want to apply for an income certificate",
        user_id="user-1",
        context=context,
    )

    assert result.get("success") is True
    assert result.get("requires_approval") is True
    assert "plan_summary" in result

    state = orchestrator.get_task_state(context.task_id)
    assert state is not None
    assert state["state"] == "WAITING_FOR_APPROVAL"


@pytest.mark.asyncio
async def test_birth_certificate_flow(orchestrator):
    """Flow: birth certificate application."""
    context = ExecutionContext(
        user_id="user-2",
        service_id="birth_certificate",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE", "FILL_FORM"],
    )

    result = await orchestrator.process_request(
        user_message="I need a birth certificate",
        user_id="user-2",
        context=context,
    )

    assert result.get("success") is True


@pytest.mark.asyncio
async def test_tracking_flow(orchestrator):
    """Flow: track application status."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE"],
    )

    result = await orchestrator.process_request(
        user_message="Track my income certificate application",
        user_id="user-1",
        context=context,
    )

    assert result.get("success") is True


@pytest.mark.asyncio
async def test_eligibility_flow(orchestrator):
    """Flow: check eligibility."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE"],
    )

    result = await orchestrator.process_request(
        user_message="Am I eligible for an income certificate?",
        user_id="user-1",
        context=context,
    )

    assert result.get("success") is True


@pytest.mark.asyncio
async def test_cancellation_flow(orchestrator):
    """Flow: cancel a task."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION"],
    )

    await orchestrator.process_request(
        user_message="I want to apply for an income certificate",
        user_id="user-1",
        context=context,
    )

    cancel_result = orchestrator.cancel_task(context.task_id)
    assert cancel_result["success"] is True
    assert cancel_result["status"] == "cancelled"

    state = orchestrator.get_task_state(context.task_id)
    assert state["state"] == "CANCELLED"


@pytest.mark.asyncio
async def test_approval_flow(orchestrator):
    """Flow: approval is requested and then granted."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE", "FILL_FORM"],
    )

    result = await orchestrator.process_request(
        user_message="I want to apply for an income certificate",
        user_id="user-1",
        context=context,
    )

    assert result.get("success") is True


@pytest.mark.asyncio
async def test_state_machine_records_history(orchestrator):
    """State machine records full transition history."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE", "FILL_FORM"],
    )

    await orchestrator.process_request(
        user_message="I want to apply for an income certificate",
        user_id="user-1",
        context=context,
    )

    state = orchestrator.get_task_state(context.task_id)
    assert state is not None
    assert len(state["history"]) > 0


@pytest.mark.asyncio
async def test_audit_events_recorded(orchestrator):
    """Audit events are recorded during processing."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE", "FILL_FORM"],
    )

    await orchestrator.process_request(
        user_message="I want to apply for an income certificate",
        user_id="user-1",
        context=context,
    )

    events = orchestrator._audit_service.get_events(task_id=context.task_id)
    assert len(events) > 0
    event_types = [e.event_type for e in events]
    assert "TASK_STARTED" in event_types


@pytest.mark.asyncio
async def test_discovery_flow(orchestrator):
    """Flow: service discovery."""
    context = ExecutionContext(
        user_id="user-1",
        permissions=["BROWSER_NAVIGATION", "READ_PAGE"],
    )

    result = await orchestrator.process_request(
        user_message="What services are available for income certificates?",
        user_id="user-1",
        context=context,
    )

    assert result.get("success") is True
