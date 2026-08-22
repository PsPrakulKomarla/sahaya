from abc import ABC, abstractmethod
from packages.agent.models.tasks import WorkflowStep, ExecutionContext


class StepHandler(ABC):
    """Interface for workflow step handlers."""

    @abstractmethod
    def can_handle(self, step_type: str) -> bool:
        pass

    @abstractmethod
    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        pass
