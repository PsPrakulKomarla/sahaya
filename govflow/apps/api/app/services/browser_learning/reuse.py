"""ReuseMode - executes a learned workflow on a live website.

When a known workflow exists:
1. Retrieve workflow
2. Compare expected context with current page
3. Execute steps
4. Verify every important step
5. Record results
6. Update confidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from packages.browser.interfaces.agent import BrowserAgent, BrowserResult
from packages.browser.interfaces.models import ElementType, PageModel
from app.core.logging import get_logger
from app.services.workflow_memory.models import (
    BrowserActionType,
    LearnableWorkflowStep,
    WorkflowDefinition,
    WorkflowStatus,
)
from app.services.workflow_memory.service import WorkflowMemoryService
from app.services.browser_learning.recovery import RecoveryResult, WorkflowRecoveryEngine
from app.services.browser_learning.change_detector import ChangeDetection

logger = get_logger(__name__)


@dataclass
class StepExecution:
    """Result of executing a single workflow step."""

    step_id: str
    success: bool
    recovered: bool = False
    confidence: float = 0.0
    error: Optional[str] = None
    page_after: Optional[PageModel] = None


@dataclass
class WorkflowExecution:
    """Result of executing a complete workflow."""

    workflow_id: str
    success: bool
    steps_executed: int = 0
    steps_recovered: int = 0
    step_results: List[StepExecution] = field(default_factory=list)
    error: Optional[str] = None
    final_page: Optional[PageModel] = None


class ReuseMode:
    """Executes a learned workflow on a live website.

    This is the core reuse capability: load a stored workflow, verify
    each step against the live page, and execute it with recovery.
    """

    def __init__(
        self,
        browser: BrowserAgent,
        memory_service: WorkflowMemoryService,
        recovery_engine: Optional[WorkflowRecoveryEngine] = None,
    ):
        self._browser = browser
        self._memory = memory_service
        self._recovery = recovery_engine or WorkflowRecoveryEngine(browser)

    async def execute(
        self,
        workflow: WorkflowDefinition,
        verify_each_step: bool = True,
    ) -> WorkflowExecution:
        """Execute a learned workflow step by step."""
        logger.info(
            "workflow_reuse_started",
            workflow_id=workflow.workflow_id,
            steps=len(workflow.steps),
        )

        execution = WorkflowExecution(
            workflow_id=workflow.workflow_id or "",
            success=True,
        )

        for step in workflow.steps:
            result = await self._execute_step(step, verify_each_step, workflow)
            execution.step_results.append(result)
            execution.steps_executed += 1

            if result.recovered:
                execution.steps_recovered += 1

            if not result.success and not step.optional:
                execution.success = False
                execution.error = (
                    f"Step {step.step_id} failed: {result.error}"
                )
                logger.error(
                    "workflow_step_failed",
                    step_id=step.step_id,
                    error=result.error,
                )
                break

            if result.page_after:
                execution.final_page = result.page_after

        # Record execution result
        if workflow.workflow_id:
            await self._memory.record_execution(
                workflow_id=__import__("uuid").UUID(workflow.workflow_id),
                success=execution.success,
                recovered=execution.steps_recovered > 0,
            )

        logger.info(
            "workflow_reuse_completed",
            workflow_id=workflow.workflow_id,
            success=execution.success,
            steps_executed=execution.steps_executed,
            steps_recovered=execution.steps_recovered,
        )

        return execution

    async def _execute_step(
        self,
        step: LearnableWorkflowStep,
        verify: bool,
        workflow: WorkflowDefinition,
    ) -> StepExecution:
        """Execute a single workflow step with verification and recovery."""
        # Verify step if requested
        if verify:
            page = await self._browser.inspect()
            verification = await self._verify_step(step, page)
            if not verification.success:
                # Attempt recovery
                recovery = await self._recovery.attempt_recovery(step, page, workflow)
                if recovery.success and recovery.recovered_step:
                    step = recovery.recovered_step
                elif recovery.needs_human:
                    return StepExecution(
                        step_id=step.step_id,
                        success=False,
                        error=f"Recovery needs human assistance: {recovery.reason}",
                    )
                else:
                    return StepExecution(
                        step_id=step.step_id,
                        success=False,
                        error=f"Recovery failed: {recovery.reason}",
                    )

        # Execute the action
        result = await self._perform_action(step)
        page_after = await self._browser.inspect() if result.success else None

        return StepExecution(
            step_id=step.step_id,
            success=result.success,
            error=result.error,
            page_after=page_after,
        )

    async def _verify_step(
        self, step: LearnableWorkflowStep, page: PageModel
    ) -> StepExecution:
        """Verify that the expected element exists on the page."""
        target = step.target
        element = page.find_element(
            role=ElementType(target.role) if target.role else None,
            text=target.text,
        )
        if element:
            return StepExecution(step_id=step.step_id, success=True)
        return StepExecution(
            step_id=step.step_id,
            success=False,
            error=f"Expected element not found: {target.text or target.role}",
        )

    async def _perform_action(self, step: LearnableWorkflowStep) -> BrowserResult:
        """Perform the browser action for a workflow step."""
        action = step.action
        target_text = step.target.text or step.target.label or step.target.description or ""

        if action == BrowserActionType.CLICK:
            return await self._browser.click(
                target_text, selector=step.selector_hint
            )
        elif action == BrowserActionType.FILL:
            return await self._browser.type_text(
                target_text, step.input_value or "", selector=step.selector_hint
            )
        elif action == BrowserActionType.SELECT:
            return await self._browser.select(
                target_text, step.input_value or "", selector=step.selector_hint
            )
        elif action == BrowserActionType.UPLOAD:
            return await self._browser.upload(
                target_text, step.input_value or "", selector=step.selector_hint
            )
        elif action == BrowserActionType.NAVIGATE:
            url = step.target.text or step.input_value or ""
            return await self._browser.navigate(url)
        elif action == BrowserActionType.SCROLL:
            return await self._browser.scroll()
        elif action == BrowserActionType.WAIT:
            return await self._browser.wait(2.0)
        elif action == BrowserActionType.GO_BACK:
            return await self._browser.go_back()
        elif action == BrowserActionType.SCREENSHOT:
            return await self._browser.screenshot()
        else:
            return BrowserResult(
                success=False,
                error=f"Unsupported action: {action.value}",
            )
