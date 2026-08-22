"""StepHandler interface and StepHandlerRegistry.

Each handler is independently testable. New handlers can be added without
modifying the TaskExecutor.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from packages.agent.executor.context import ExecutionContext
from packages.agent.planner.models import StepType, WorkflowStep


class StepHandler(ABC):
    """Interface for workflow step handlers.

    Each handler processes a specific type of workflow step.
    Handlers receive the step and context, and return a result dict.
    """

    @abstractmethod
    def can_handle(self, step_type: StepType) -> bool:
        """Check if this handler can handle the given step type."""
        pass

    @abstractmethod
    async def execute(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Execute the step and return the result.

        Args:
            step: The workflow step to execute.
            context: The current execution context.

        Returns:
            A dict with the execution result.
            Must include at least {"success": True/False}.
        """
        pass


class StepHandlerRegistry:
    """Registry of step handlers.

    Maps step types to handlers. The TaskExecutor uses this registry
    to find the correct handler for each step.
    """

    def __init__(self) -> None:
        self._handlers: Dict[StepType, StepHandler] = {}
        self._fallback: Optional[StepHandler] = None

    def register(self, step_type: StepType, handler: StepHandler) -> None:
        """Register a handler for a step type."""
        self._handlers[step_type] = handler

    def register_fallback(self, handler: StepHandler) -> None:
        """Register a fallback handler for unregistered step types."""
        self._fallback = handler

    def get_handler(self, step_type: StepType) -> Optional[StepHandler]:
        """Get the handler for a step type."""
        return self._handlers.get(step_type)

    def get_handler_or_fallback(self, step_type: StepType) -> Optional[StepHandler]:
        """Get the handler, falling back to the default if not found."""
        return self._handlers.get(step_type) or self._fallback

    def has_handler(self, step_type: StepType) -> bool:
        """Check if a handler is registered for a step type."""
        return step_type in self._handlers

    def list_handlers(self) -> Dict[str, str]:
        """List all registered handlers."""
        return {
            st.value: type(h).__name__
            for st, h in self._handlers.items()
        }
