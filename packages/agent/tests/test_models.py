import pytest
from packages.agent.models.tasks import (
    AgentState,
    StepType,
    StepStatus,
    TaskStatus,
    TaskType,
    RetryPolicy,
    WorkflowStep,
    WorkflowPlan,
    ExecutionContext,
    TaskResult,
    AgentTask,
)
from packages.agent.models.errors import (
    AgentError,
    InvalidStateTransition,
    StepExecutionError,
    ApprovalRequired,
    ApprovalExpired,
    PermissionDenied,
    BrowserUnavailable,
    BrowserActionFailed,
    TaskCancelled,
    WorkflowInvalid,
)


class TestAgentModels:
    def test_workflow_step_creation(self):
        step = WorkflowStep(
            id="test_step",
            type=StepType.DISCOVER_SERVICE,
            description="Test step",
        )
        assert step.id == "test_step"
        assert step.type == StepType.DISCOVER_SERVICE
        assert step.status == StepStatus.PENDING

    def test_workflow_step_defaults(self):
        step = WorkflowStep(type=StepType.BROWSER_EXECUTION)
        assert step.id is not None
        assert step.dependencies == []
        assert step.requires_approval is False

    def test_workflow_plan_creation(self):
        plan = WorkflowPlan(
            task_type=TaskType.NEW_APPLICATION,
            service_id="test_service",
            steps=[
                WorkflowStep(id="s1", type=StepType.DISCOVER_SERVICE),
                WorkflowStep(id="s2", type=StepType.BROWSER_EXECUTION, dependencies=["s1"]),
            ],
        )
        assert plan.task_type == TaskType.NEW_APPLICATION
        assert len(plan.steps) == 2

    def test_workflow_plan_get_step(self):
        plan = WorkflowPlan(
            task_type=TaskType.NEW_APPLICATION,
            service_id="test",
            steps=[WorkflowStep(id="s1", type=StepType.DISCOVER_SERVICE)],
        )
        assert plan.get_step("s1") is not None
        assert plan.get_step("nonexistent") is None

    def test_workflow_plan_get_ready_steps(self):
        plan = WorkflowPlan(
            task_type=TaskType.NEW_APPLICATION,
            service_id="test",
            steps=[
                WorkflowStep(id="s1", type=StepType.DISCOVER_SERVICE),
                WorkflowStep(id="s2", type=StepType.BROWSER_EXECUTION, dependencies=["s1"]),
            ],
        )
        ready = plan.get_ready_steps()
        assert len(ready) == 1
        assert ready[0].id == "s1"

    def test_workflow_plan_is_complete(self):
        plan = WorkflowPlan(
            task_type=TaskType.NEW_APPLICATION,
            service_id="test",
            steps=[
                WorkflowStep(id="s1", type=StepType.DISCOVER_SERVICE, status=StepStatus.COMPLETED),
            ],
        )
        assert plan.is_complete() is True

    def test_workflow_plan_has_failed(self):
        plan = WorkflowPlan(
            task_type=TaskType.NEW_APPLICATION,
            service_id="test",
            steps=[
                WorkflowStep(id="s1", type=StepType.DISCOVER_SERVICE, status=StepStatus.FAILED),
            ],
        )
        assert plan.has_failed() is True

    def test_retry_policy(self):
        policy = RetryPolicy(max_retries=3, retryable=True)
        assert policy.max_retries == 3
        assert policy.retryable is True

    def test_execution_context(self):
        ctx = ExecutionContext(
            task_id="t1",
            user_id="u1",
            service_id="s1",
        )
        assert ctx.task_id == "t1"
        assert ctx.permissions == []

    def test_task_result(self):
        result = TaskResult(
            task_id="t1",
            status=TaskStatus.COMPLETED,
        )
        assert result.status == TaskStatus.COMPLETED

    def test_agent_task_creation(self):
        task = AgentTask(
            user_id="u1",
            original_request="test request",
        )
        assert task.user_id == "u1"
        assert task.state == AgentState.CREATED
        assert task.status == TaskStatus.CREATED


class TestAgentErrors:
    def test_agent_error(self):
        err = AgentError("test", code="TEST_ERROR")
        assert str(err) == "test"
        assert err.code == "TEST_ERROR"

    def test_invalid_state_transition(self):
        err = InvalidStateTransition("STATE_A", "STATE_B")
        assert "STATE_A" in str(err)
        assert "STATE_B" in str(err)
        assert err.code == "INVALID_STATE_TRANSITION"

    def test_step_execution_error(self):
        err = StepExecutionError("s1", "CLICK", "timeout")
        assert err.code == "STEP_EXECUTION_ERROR"

    def test_approval_required(self):
        err = ApprovalRequired("SUBMIT", "Submit application")
        assert err.code == "APPROVAL_REQUIRED"

    def test_task_cancelled(self):
        err = TaskCancelled("t1")
        assert err.code == "TASK_CANCELLED"

    def test_workflow_invalid(self):
        err = WorkflowInvalid("No steps")
        assert err.code == "WORKFLOW_INVALID"
