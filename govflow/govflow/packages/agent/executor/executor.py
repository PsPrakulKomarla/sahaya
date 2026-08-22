"""TaskExecutor executes a WorkflowPlan through registered step handlers.

It does NOT contain step-specific logic. Each step is handled by a
registered StepHandler found through the StepHandlerRegistry.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from packages.agent.executor.context import ExecutionContext
from packages.agent.executor.handlers import StepHandlerRegistry
from packages.agent.errors import ApprovalRequired, StepExecutionError
from packages.agent.planner.models import StepStatus, WorkflowPlan, WorkflowStep

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes workflow plans through registered step handlers.

    The executor orchestrates step execution, handles failures,
    and records results. It does NOT contain browser-specific or
    service-specific logic.
    """

    def __init__(
        self,
        handler_registry: StepHandlerRegistry,
        on_step_complete: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
        on_step_failed: Optional[Callable[[str, str, str], None]] = None,
    ):
        self._registry = handler_registry
        self._on_step_complete = on_step_complete
        self._on_step_failed = on_step_failed

    async def execute_plan(
        self,
        plan: WorkflowPlan,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Execute all steps in a workflow plan.

        Returns a summary of the execution.
        """
        results: List[Dict[str, Any]] = []

        while not plan.is_complete():
            next_step = plan.get_next_step()
            if next_step is None:
                if plan.has_failed_steps():
                    return {
                        "success": False,
                        "error": "Workflow has failed steps with no recoverable path",
                        "results": results,
                        "plan_summary": plan.summary(),
                    }
                break

            result = await self.execute_step(next_step, context, plan)
            results.append(result)

            if not result.get("success", False):
                if next_step.retry_policy.retryable and next_step.retry_policy.max_retries > 0:
                    next_step.retry_policy.max_retries -= 1
                    next_step.status = StepStatus.PENDING
                    continue
                plan.mark_step_failed(next_step.id, result)
                if self._on_step_failed:
                    self._on_step_failed(next_step.id, next_step.type.value, str(result.get("error", "")))
                return {
                    "success": False,
                    "failed_step": next_step.id,
                    "error": result.get("error", "Unknown error"),
                    "results": results,
                    "plan_summary": plan.summary(),
                }

        return {
            "success": plan.is_complete(),
            "results": results,
            "plan_summary": plan.summary(),
        }

    async def execute_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        plan: Optional[WorkflowPlan] = None,
    ) -> Dict[str, Any]:
        """Execute a single workflow step.

        Finds the appropriate handler and executes it.
        """
        handler = self._registry.get_handler_or_fallback(step.type)
        if handler is None:
            return {
                "success": False,
                "error": f"No handler registered for step type: {step.type.value}",
                "step_id": step.id,
            }

        step_context = context.with_step(step.id)
        step.mark_running()

        try:
            result = await handler.execute(step, step_context)
            step.mark_completed(result)

            if self._on_step_complete:
                self._on_step_complete(step.id, step.type.value, result)

            return result

        except ApprovalRequired:
            step.mark_waiting_approval()
            raise

        except Exception as e:
            error_msg = str(e)
            step.mark_failed({"error": error_msg})
            logger.error("Step %s failed: %s", step.id, error_msg)

            if self._on_step_failed:
                self._on_step_failed(step.id, step.type.value, error_msg)

            return {
                "success": False,
                "error": error_msg,
                "step_id": step.id,
            }

    async def execute_up_to(
        self,
        plan: WorkflowPlan,
        context: ExecutionContext,
        stop_before_step_id: str,
    ) -> Dict[str, Any]:
        """Execute steps until reaching a specific step (exclusive).

        Used when we need to stop before a step that requires approval.
        """
        results: List[Dict[str, Any]] = []

        while not plan.is_complete():
            next_step = plan.get_next_step()
            if next_step is None or next_step.id == stop_before_step_id:
                break

            result = await self.execute_step(next_step, context, plan)
            results.append(result)

            if not result.get("success", False):
                return {
                    "success": False,
                    "failed_step": next_step.id,
                    "error": result.get("error", "Unknown error"),
                    "results": results,
                    "plan_summary": plan.summary(),
                }

        return {
            "success": True,
            "stopped_before": stop_before_step_id,
            "results": results,
            "plan_summary": plan.summary(),
        }
