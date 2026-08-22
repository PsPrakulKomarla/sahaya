"""Tests for the TaskPlanner."""
import pytest
from packages.agent.planner.models import StepType, StepStatus, WorkflowPlan, WorkflowStep
from packages.agent.planner.planner import TaskPlanner
from packages.agent.errors import WorkflowInvalid
from packages.services.intent.models import Intent, IntentType, Jurisdiction
from packages.services.registry.models import ServiceResolution


@pytest.fixture
def planner():
    return TaskPlanner()


@pytest.fixture
def income_resolution():
    return ServiceResolution(
        status="RESOLVED",
        service_id="income_certificate",
        service_name="Income Certificate",
        capabilities=["new_application", "track_application", "eligibility_check", "document_requirements"],
    )


@pytest.fixture
def passport_resolution():
    return ServiceResolution(
        status="RESOLVED",
        service_id="passport_renewal",
        service_name="Passport Renewal",
        capabilities=["renewal", "track_application", "document_requirements"],
    )


class TestPlannerApplicationWorkflow:
    def test_new_application_plan(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="income certificate",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        assert plan.task_type == "NEW_APPLICATION"
        assert plan.service_id == "income_certificate"
        assert len(plan.steps) > 0

        step_types = [s.type for s in plan.steps]
        assert StepType.DISCOVER_SERVICE in step_types
        assert StepType.GET_REQUIREMENTS in step_types
        assert StepType.CHECK_ELIGIBILITY in step_types
        assert StepType.VALIDATE_DOCUMENTS in step_types
        assert StepType.BROWSER_EXECUTION in step_types
        assert StepType.HUMAN_REVIEW in step_types
        assert StepType.SUBMIT in step_types
        assert StepType.COMPLETE in step_types

    def test_application_plan_has_dependencies(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="income certificate",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        requirements_step = next(s for s in plan.steps if s.id == "requirements")
        assert "discover" in requirements_step.dependencies

        eligibility_step = next(s for s in plan.steps if s.id == "eligibility")
        assert "requirements" in eligibility_step.dependencies

        submit_step = next(s for s in plan.steps if s.id == "submit")
        assert submit_step.requires_approval is True

    def test_application_plan_submit_not_retryable(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="income certificate",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        submit_step = next(s for s in plan.steps if s.id == "submit")
        assert submit_step.retry_policy.max_retries == 0
        assert submit_step.retry_policy.retryable is False


class TestPlannerUpdateWorkflow:
    def test_update_plan(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.UPDATE_RECORD,
            service_query="income certificate",
            operation=IntentType.UPDATE_RECORD,
        )
        plan = planner.plan(intent, income_resolution)

        assert plan.task_type == "UPDATE_RECORD"
        step_types = [s.type for s in plan.steps]
        assert StepType.UPDATE_RECORD not in step_types
        assert StepType.BROWSER_EXECUTION in step_types
        assert StepType.SUBMIT in step_types


class TestPlannerRenewalWorkflow:
    def test_renewal_plan(self, planner, passport_resolution):
        intent = Intent(
            intent=IntentType.RENEWAL,
            service_query="passport renewal",
            operation=IntentType.RENEWAL,
        )
        plan = planner.plan(intent, passport_resolution)

        assert plan.task_type == "RENEWAL"
        assert plan.service_id == "passport_renewal"
        step_types = [s.type for s in plan.steps]
        assert StepType.RENEW not in step_types
        assert StepType.CHECK_ELIGIBILITY in step_types


class TestPlannerTrackingWorkflow:
    def test_tracking_plan(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.TRACK_APPLICATION,
            service_query="income certificate",
            operation=IntentType.TRACK_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        assert plan.task_type == "TRACK_APPLICATION"
        step_types = [s.type for s in plan.steps]
        assert StepType.EXTRACT_DATA in step_types
        assert StepType.SUBMIT not in step_types


class TestPlannerGrievanceWorkflow:
    def test_grievance_plan(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.RAISE_GRIEVANCE,
            service_query="income certificate",
            operation=IntentType.RAISE_GRIEVANCE,
        )
        plan = planner.plan(intent, income_resolution)

        assert plan.task_type == "RAISE_GRIEVANCE"
        step_types = [s.type for s in plan.steps]
        assert StepType.RAISE_GRIEVANCE not in step_types
        assert StepType.SUBMIT in step_types


class TestPlannerDiscovery:
    def test_discovery_plan(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.SERVICE_DISCOVERY,
            service_query="what services are available",
            operation=IntentType.SERVICE_DISCOVERY,
        )
        plan = planner.plan(intent, income_resolution)

        assert len(plan.steps) == 2
        assert plan.steps[0].type == StepType.DISCOVER_SERVICE
        assert plan.steps[1].type == StepType.COMPLETE


class TestPlannerErrors:
    def test_clarification_required_raises(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.CLARIFICATION_REQUIRED,
            service_query="",
            operation=IntentType.CLARIFICATION_REQUIRED,
        )
        with pytest.raises(WorkflowInvalid):
            planner.plan(intent, income_resolution)


class TestWorkflowPlan:
    def test_get_step(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="test",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        discover = plan.get_step("discover")
        assert discover is not None
        assert discover.type == StepType.DISCOVER_SERVICE

        assert plan.get_step("nonexistent") is None

    def test_get_ready_steps(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="test",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        ready = plan.get_ready_steps()
        assert len(ready) >= 1
        assert ready[0].id == "discover"

    def test_is_complete(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="test",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        assert not plan.is_complete()

        for step in plan.steps:
            step.mark_completed()

        assert plan.is_complete()

    def test_mark_step_completed(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="test",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)

        plan.mark_step_completed("discover", {"url": "https://example.gov.in"})
        step = plan.get_step("discover")
        assert step.status == StepStatus.COMPLETED
        assert step.output_data["url"] == "https://example.gov.in"

    def test_summary(self, planner, income_resolution):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="test",
            operation=IntentType.NEW_APPLICATION,
        )
        plan = planner.plan(intent, income_resolution)
        s = plan.summary()

        assert "total_steps" in s
        assert "completed" in s
        assert "is_complete" in s
