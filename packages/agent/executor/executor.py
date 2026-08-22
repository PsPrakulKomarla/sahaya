from datetime import datetime
from packages.agent.executor.registry import StepHandlerRegistry
from packages.agent.executor.step_handlers import (
    DiscoverServiceHandler,
    GetRequirementsHandler,
    CheckEligibilityHandler,
    ValidateDocumentsHandler,
    PrepareApplicationHandler,
    BrowserExecutionHandler,
    ExtractDataHandler,
    HumanReviewHandler,
    SubmitHandler,
    TrackApplicationHandler,
    RaiseGrievanceHandler,
    UpdateRecordHandler,
    RenewHandler,
    CompleteHandler,
)
from packages.agent.models.tasks import WorkflowPlan, WorkflowStep, StepStatus, ExecutionContext
from packages.agent.models.errors import StepExecutionError


def create_default_registry() -> StepHandlerRegistry:
    registry = StepHandlerRegistry()
    for handler in [
        DiscoverServiceHandler(),
        GetRequirementsHandler(),
        CheckEligibilityHandler(),
        ValidateDocumentsHandler(),
        PrepareApplicationHandler(),
        BrowserExecutionHandler(),
        ExtractDataHandler(),
        HumanReviewHandler(),
        SubmitHandler(),
        TrackApplicationHandler(),
        RaiseGrievanceHandler(),
        UpdateRecordHandler(),
        RenewHandler(),
        CompleteHandler(),
    ]:
        registry.register(handler)
    return registry


class TaskExecutor:
    """Executes workflow steps through registered handlers."""

    def __init__(self, handler_registry: StepHandlerRegistry = None):
        self.registry = handler_registry or create_default_registry()

    async def execute_step(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        handler = self.registry.get_handler(step.type.value)
        if handler is None:
            raise StepExecutionError(
                step_id=step.id,
                step_type=step.type.value,
                reason=f"No handler registered for step type {step.type.value}",
            )

        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.utcnow()
        context.current_step = step.id

        try:
            result = await handler.execute(step, context)
            step.output_data = result
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            return result
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            raise StepExecutionError(
                step_id=step.id,
                step_type=step.type.value,
                reason=str(e),
            )

    async def execute_plan(self, plan: WorkflowPlan, context: ExecutionContext) -> dict:
        results = {}
        max_iterations = len(plan.steps) * 2
        iteration = 0

        while not plan.is_complete() and iteration < max_iterations:
            iteration += 1
            ready_steps = plan.get_ready_steps()
            if not ready_steps:
                break

            for step in ready_steps:
                try:
                    result = await self.execute_step(step, context)
                    results[step.id] = result
                except StepExecutionError:
                    continue

        return results
