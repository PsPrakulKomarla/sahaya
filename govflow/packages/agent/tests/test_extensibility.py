"""Extensibility tests.

Tests that new services and browser providers can be added without
modifying the core agent architecture.
"""
import pytest
from packages.agent.planner.planner import TaskPlanner
from packages.agent.planner.models import StepType, WorkflowPlan
from packages.agent.executor.handlers import StepHandlerRegistry
from packages.agent.executor.handlers_impl import register_default_handlers
from packages.agent.executor.executor import TaskExecutor
from packages.agent.executor.context import ExecutionContext, Permission
from packages.agent.safety.engine import SafetyPolicyEngine, SafetyDecisionType
from packages.services.intent.models import Intent, IntentType
from packages.services.registry.models import ServiceResolution
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import (
    ServiceCapability,
    ServiceMetadata,
    ServiceResponse,
    WorkflowStep,
)


class MockPassportRenewalAdapter(GovernmentServiceAdapter):
    """New mock service — passport renewal.

    Tests that a new service can be registered without modifying
    the core agent architecture.
    """

    def metadata(self) -> ServiceMetadata:
        return ServiceMetadata(
            service_id="passport_renewal",
            display_name="Passport Renewal",
            description="Renew an Indian passport",
            department="Ministry of External Affairs",
            jurisdiction="India",
            official_portal="https://example.passport.gov.in",
            capabilities=[
                ServiceCapability.DOCUMENT_REQUIREMENTS,
                ServiceCapability.RENEW,
                ServiceCapability.TRACK_APPLICATION,
            ],
            required_documents=[
                {"document_type": "passport", "display_name": "Current Passport", "description": "Your current passport for renewal", "mandatory": True},
                {"document_type": "photograph", "display_name": "Photograph", "description": "Recent passport-size photograph", "mandatory": True},
            ],
        )

    async def discover(self, query, jurisdiction=None):
        return ServiceResponse(
            success=True,
            data={"service_id": "passport_renewal", "display_name": "Passport Renewal"},
        )

    def _generate_workflow_steps(self, operation):
        return [
            WorkflowStep(id="discover", action="DISCOVER_PORTAL", description="Find portal"),
            WorkflowStep(id="requirements", action="GET_REQUIREMENTS", description="Get docs needed"),
            WorkflowStep(id="documents", action="VALIDATE_DOCUMENTS", description="Check passport"),
            WorkflowStep(id="renew", action="RENEW_PASSPORT", description="Submit renewal"),
            WorkflowStep(id="track", action="TRACK_STATUS", description="Track application"),
        ]


class TestServiceExtensibility:
    """New services can be registered without modifying the planner."""

    def test_new_service_has_capabilities(self):
        adapter = MockPassportRenewalAdapter()
        caps = adapter.get_capabilities()
        assert ServiceCapability.RENEW in caps
        assert ServiceCapability.TRACK_APPLICATION in caps
        assert ServiceCapability.DOCUMENT_REQUIREMENTS in caps

    def test_planner_handles_renewal(self):
        planner = TaskPlanner()
        intent = Intent(
            intent=IntentType.RENEWAL,
            service_query="passport renewal",
            operation=IntentType.RENEWAL,
        )
        resolution = ServiceResolution(
            status="RESOLVED",
            service_id="passport_renewal",
            service_name="Passport Renewal",
            capabilities=["renewal", "track_application", "document_requirements"],
        )
        plan = planner.plan(intent, resolution)

        assert plan.service_id == "passport_renewal"
        step_types = [s.type for s in plan.steps]
        assert StepType.CHECK_ELIGIBILITY in step_types
        assert StepType.VALIDATE_DOCUMENTS in step_types
        assert StepType.TRACK_APPLICATION in step_types

    def test_planner_handles_tracking(self):
        planner = TaskPlanner()
        intent = Intent(
            intent=IntentType.TRACK_APPLICATION,
            service_query="passport renewal",
            operation=IntentType.TRACK_APPLICATION,
        )
        resolution = ServiceResolution(
            status="RESOLVED",
            service_id="passport_renewal",
            service_name="Passport Renewal",
            capabilities=["track_application"],
        )
        plan = planner.plan(intent, resolution)

        assert plan.service_id == "passport_renewal"
        step_types = [s.type for s in plan.steps]
        assert StepType.EXTRACT_DATA in step_types

    def test_new_service_adapter_interface(self):
        adapter = MockPassportRenewalAdapter()
        assert isinstance(adapter, GovernmentServiceAdapter)
        assert adapter.supports_capability(ServiceCapability.RENEW)
        assert not adapter.supports_capability(ServiceCapability.NEW_APPLICATION)


class TestBrowserProviderExtensibility:
    """Both MockBrowserAgent and PlaywrightBrowserAgent work through
    the same BrowserAgent interface."""

    def test_mock_browser_through_interface(self):
        from packages.browser.interfaces.agent import BrowserAgent
        from packages.browser.mock.agent import MockBrowserAgent

        agent = MockBrowserAgent()
        assert isinstance(agent, BrowserAgent)

    def test_playwright_browser_through_interface(self):
        from packages.browser.interfaces.agent import BrowserAgent
        from packages.browser.playwright.agent import PlaywrightBrowserAgent

        agent = PlaywrightBrowserAgent()
        assert isinstance(agent, BrowserAgent)

    def test_orchestrator_uses_interface(self):
        from packages.agent.orchestrator import AgentOrchestrator
        from packages.browser.interfaces.agent import BrowserAgent
        from packages.browser.mock.agent import MockBrowserAgent
        from packages.services.intent.engine import RuleBasedIntentEngine
        from packages.services.registry.resolver import ServiceResolver

        browser = MockBrowserAgent()
        orchestrator = AgentOrchestrator(
            intent_engine=RuleBasedIntentEngine(),
            service_resolver=ServiceResolver(),
            browser_agent=browser,
        )
        assert orchestrator._browser_agent is browser
        assert isinstance(orchestrator._browser_agent, BrowserAgent)


class TestStepHandlerExtensibility:
    """New step handlers can be registered without modifying the executor."""

    def test_custom_handler_registration(self):
        from packages.agent.executor.handlers import StepHandler

        class CustomStepHandler(StepHandler):
            def can_handle(self, step_type):
                return step_type == StepType.UPDATE_RECORD

            async def execute(self, step, context):
                return {"success": True, "custom": True}

        registry = StepHandlerRegistry()
        register_default_handlers(registry)

        custom = CustomStepHandler()
        registry.register(StepType.UPDATE_RECORD, custom)

        handler = registry.get_handler(StepType.UPDATE_RECORD)
        assert isinstance(handler, CustomStepHandler)


class TestSafetyExtensibility:
    """New sensitive actions can be registered."""

    def test_register_custom_sensitive_action(self):
        engine = SafetyPolicyEngine()
        engine.register_sensitive("CUSTOM_SENSITIVE_ACTION")
        assert engine.is_sensitive("CUSTOM_SENSITIVE_ACTION")

        decision = engine.evaluate("CUSTOM_SENSITIVE_ACTION")
        assert decision.decision == SafetyDecisionType.REQUIRE_APPROVAL

    def test_register_denied_action(self):
        engine = SafetyPolicyEngine()
        engine.register_denied("BLOCKED_ACTION")
        decision = engine.evaluate("BLOCKED_ACTION")
        assert decision.decision == SafetyDecisionType.DENY
