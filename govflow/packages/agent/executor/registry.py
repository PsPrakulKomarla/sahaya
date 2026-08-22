from typing import Dict, Optional
from packages.agent.executor.handlers import StepHandler
from packages.agent.models.tasks import StepType


class StepHandlerRegistry:
    """Registry for step handlers."""

    def __init__(self):
        self._handlers: Dict[str, StepHandler] = {}

    def register(self, handler: StepHandler) -> None:
        for step_type in StepType:
            if handler.can_handle(step_type.value):
                self._handlers[step_type.value] = handler

    def get_handler(self, step_type: str) -> Optional[StepHandler]:
        return self._handlers.get(step_type)

    def has_handler(self, step_type: str) -> bool:
        return step_type in self._handlers
