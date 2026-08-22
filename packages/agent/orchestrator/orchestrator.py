from datetime import datetime
from typing import Optional, Dict, Any
from packages.agent.models.tasks import (
    AgentTask,
    AgentState,
    TaskStatus,
    TaskType,
    WorkflowPlan,
    ExecutionContext,
)
from packages.agent.models.errors import (
    AgentError,
    InvalidStateTransition,
    ApprovalRequired,
    TaskCancelled,
    WorkflowInvalid,
)
from packages.agent.state_machine.machine import AgentStateMachine
from packages.agent.planner.planner import TaskPlanner
from packages.agent.executor.executor import TaskExecutor
from packages.agent.safety.engine import SafetyPolicyEngine, SafetyDecision
from packages.agent.approval.service import ApprovalService, ApprovalStatus
from packages.services.intent.models import Intent, IntentContext
from packages.services.intent.engine import RuleBasedIntentEngine
from packages.services.registry.resolver import ServiceResolver
from packages.services.registry.models import ResolutionStatus


class AgentOrchestrator:
    """Coordinates the complete agent task lifecycle."""

    def __init__(
        self,
        intent_engine: Optional[RuleBasedIntentEngine] = None,
        resolver: Optional[ServiceResolver] = None,
        planner: Optional[TaskPlanner] = None,
        executor: Optional[TaskExecutor] = None,
        safety_engine: Optional[SafetyPolicyEngine] = None,
        approval_service: Optional[ApprovalService] = None,
    ):
        self.intent_engine = intent_engine or RuleBasedIntentEngine()
        self.resolver = resolver or ServiceResolver()
        self.planner = planner or TaskPlanner()
        self.executor = executor or TaskExecutor()
        self.safety_engine = safety_engine or SafetyPolicyEngine()
        self.approval_service = approval_service or ApprovalService()

    async def process_request(
        self,
        message: str,
        user_id: str,
        context: Optional[IntentContext] = None,
    ) -> AgentTask:
        task = AgentTask(
            user_id=user_id,
            original_request=message,
        )
        state_machine = AgentStateMachine()

        try:
            await self._understand(task, state_machine, message, context)
            await self._resolve_service(task, state_machine)
            await self._plan(task, state_machine)
            await self._validate_plan(task, state_machine)
            await self._execute(task, state_machine)
            await self._complete(task, state_machine)
        except ApprovalRequired as e:
            task.status = TaskStatus.WAITING_FOR_APPROVAL
            task.error = str(e)
        except TaskCancelled as e:
            task.status = TaskStatus.CANCELLED
            task.error = str(e)
        except AgentError as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            if state_machine.can_transition(AgentState.FAILED):
                state_machine.transition(AgentState.FAILED)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            if state_machine.can_transition(AgentState.FAILED):
                state_machine.transition(AgentState.FAILED)

        task.state = state_machine.state
        task.updated_at = datetime.utcnow()
        return task

    async def _understand(
        self,
        task: AgentTask,
        state_machine: AgentStateMachine,
        message: str,
        context: Optional[IntentContext],
    ) -> None:
        state_machine.transition(AgentState.UNDERSTANDING)
        task.state = state_machine.state

        intent = self.intent_engine.parse(message, context)
        task.intent = intent.model_dump()
        task.service_id = intent.service_query

    async def _resolve_service(
        self,
        task: AgentTask,
        state_machine: AgentStateMachine,
    ) -> None:
        state_machine.transition(AgentState.RESOLVING_SERVICE)
        task.state = state_machine.state

        intent_data = task.intent or {}
        intent = Intent(**intent_data)
        resolution = await self.resolver.resolve_intent(intent)
        task.resolution = resolution.model_dump()

        if resolution.status != ResolutionStatus.RESOLVED:
            task.status = TaskStatus.FAILED
            task.error = f"Service resolution failed: {resolution.status}"
            raise WorkflowInvalid(resolution.reason or "Service not resolved")

        task.service_id = resolution.service_id

    async def _plan(
        self,
        task: AgentTask,
        state_machine: AgentStateMachine,
    ) -> None:
        state_machine.transition(AgentState.PLANNING)
        task.state = state_machine.state

        intent_data = task.intent or {}
        resolution_data = task.resolution or {}
        intent = Intent(**intent_data)
        from packages.services.registry.models import ServiceResolution
        resolution = ServiceResolution(**resolution_data)

        plan = self.planner.create_plan(intent, resolution)
        if not plan.steps:
            raise WorkflowInvalid("No workflow steps generated")

        task.workflow_plan = plan
        task.task_type = plan.task_type

    async def _validate_plan(
        self,
        task: AgentTask,
        state_machine: AgentStateMachine,
    ) -> None:
        state_machine.transition(AgentState.VALIDATING)
        task.state = state_machine.state

    async def _execute(
        self,
        task: AgentTask,
        state_machine: AgentStateMachine,
    ) -> None:
        state_machine.transition(AgentState.EXECUTING)
        task.state = state_machine.state
        task.status = TaskStatus.EXECUTING

        if not task.workflow_plan:
            raise WorkflowInvalid("No workflow plan to execute")

        context = ExecutionContext(
            task_id=task.task_id,
            user_id=task.user_id,
            service_id=task.service_id or "",
            jurisdiction=task.jurisdiction,
        )

        for step in task.workflow_plan.steps:
            if task.status == TaskStatus.CANCELLED:
                raise TaskCancelled(task.task_id)

            decision = self.safety_engine.evaluate(step.type)
            if decision == SafetyDecision.REQUIRE_APPROVAL:
                approval = self.approval_service.create_approval(
                    action_type=step.type.value,
                    summary={"step": step.id, "description": step.description},
                    user_id=task.user_id,
                    task_id=task.task_id,
                )
                task.status = TaskStatus.WAITING_FOR_APPROVAL
                task.state = AgentState.WAITING_FOR_APPROVAL
                raise ApprovalRequired(
                    action=step.type.value,
                    summary=f"Step '{step.description}' requires approval",
                )

            if decision == SafetyDecision.DENY:
                step.status = "FAILED"
                step.error = "Action denied by safety policy"
                continue

            try:
                await self.executor.execute_step(step, context)
            except Exception as e:
                step.status = "FAILED"
                step.error = str(e)
                continue

    async def _complete(
        self,
        task: AgentTask,
        state_machine: AgentStateMachine,
    ) -> None:
        if task.workflow_plan and task.workflow_plan.is_complete():
            state_machine.transition(AgentState.COMPLETED)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.state = state_machine.state

    async def approve_step(
        self,
        task: AgentTask,
        approval_id: str,
    ) -> bool:
        approval = self.approval_service.approve(approval_id)
        if approval is None:
            return False

        task.status = TaskStatus.EXECUTING
        return True

    async def cancel_task(self, task: AgentTask) -> None:
        task.status = TaskStatus.CANCELLED
        task.error = "Task cancelled by user"
        task.updated_at = datetime.utcnow()
