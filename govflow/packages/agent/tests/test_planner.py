import pytest
from packages.agent.planner.planner import TaskPlanner
from packages.agent.models.tasks import TaskType, StepType
from packages.services.intent.models import Intent, IntentType, Jurisdiction, Language
from packages.services.registry.models import ServiceResolution, ResolutionStatus, ResolutionJurisdiction


class TestTaskPlanner:
    @pytest.fixture
    def planner(self):
        return TaskPlanner()

    def test_new_application_plan(self, planner):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="income certificate",
            operation=IntentType.NEW_APPLICATION,
            jurisdiction=Jurisdiction(country="India", state="Karnataka"),
            language=Language.ENGLISH,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="income_certificate",
            service_name="Income Certificate",
            capabilities=["discover", "eligibility_check", "document_requirements", "new_application", "track_application"],
            workflow_version="1.0",
        )
        plan = planner.create_plan(intent, resolution)
        assert plan.task_type == TaskType.NEW_APPLICATION
        assert plan.service_id == "income_certificate"
        assert len(plan.steps) > 0
        step_types = [s.type for s in plan.steps]
        assert StepType.DISCOVER_SERVICE in step_types
        assert StepType.BROWSER_EXECUTION in step_types
        assert StepType.SUBMIT in step_types

    def test_tracking_plan(self, planner):
        intent = Intent(
            intent=IntentType.TRACK_APPLICATION,
            service_query="income certificate",
            operation=IntentType.TRACK_APPLICATION,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="income_certificate",
            capabilities=["discover", "track_application"],
        )
        plan = planner.create_plan(intent, resolution)
        assert plan.task_type == TaskType.TRACK_APPLICATION
        step_types = [s.type for s in plan.steps]
        assert StepType.TRACK_APPLICATION in step_types or StepType.BROWSER_EXECUTION in step_types

    def test_grievance_plan(self, planner):
        intent = Intent(
            intent=IntentType.RAISE_GRIEVANCE,
            service_query="income certificate",
            operation=IntentType.RAISE_GRIEVANCE,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="income_certificate",
            capabilities=["discover", "raise_grievance"],
        )
        plan = planner.create_plan(intent, resolution)
        assert plan.task_type == TaskType.RAISE_GRIEVANCE
        step_types = [s.type for s in plan.steps]
        assert StepType.SUBMIT in step_types

    def test_renewal_plan(self, planner):
        intent = Intent(
            intent=IntentType.RENEWAL,
            service_query="passport",
            operation=IntentType.RENEWAL,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="passport_renewal",
            capabilities=["discover", "document_requirements", "renew", "track_application"],
        )
        plan = planner.create_plan(intent, resolution)
        assert plan.task_type == TaskType.RENEWAL
        step_types = [s.type for s in plan.steps]
        assert StepType.RENEW in step_types or StepType.BROWSER_EXECUTION in step_types

    def test_not_resolved_returns_empty(self, planner):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="unknown service",
            operation=IntentType.NEW_APPLICATION,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.NOT_FOUND,
            reason="Service not found",
        )
        plan = planner.create_plan(intent, resolution)
        assert len(plan.steps) == 0

    def test_human_review_requires_approval(self, planner):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="income certificate",
            operation=IntentType.NEW_APPLICATION,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="income_certificate",
            capabilities=["new_application"],
        )
        plan = planner.create_plan(intent, resolution)
        review_steps = [s for s in plan.steps if s.type == StepType.HUMAN_REVIEW]
        assert len(review_steps) > 0
        assert all(s.requires_approval for s in review_steps)

    def test_complete_step_dependencies(self, planner):
        intent = Intent(
            intent=IntentType.NEW_APPLICATION,
            service_query="income certificate",
            operation=IntentType.NEW_APPLICATION,
        )
        resolution = ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id="income_certificate",
            capabilities=["new_application"],
        )
        plan = planner.create_plan(intent, resolution)
        complete_step = next((s for s in plan.steps if s.type == StepType.COMPLETE), None)
        assert complete_step is not None
        assert len(complete_step.dependencies) > 0
