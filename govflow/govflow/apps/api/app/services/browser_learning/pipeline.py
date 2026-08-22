"""Learning Pipeline - discovers, learns, and stores browser workflows.

Pipeline stages:
DISCOVER -> OBSERVE -> NORMALIZE -> UNDERSTAND -> BUILD WORKFLOW -> VALIDATE -> STORE -> ACTIVATE
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from packages.browser.interfaces.agent import BrowserAgent
from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement
from app.core.logging import get_logger
from app.services.workflow_memory.models import (
    BrowserActionType,
    ExpectedResult,
    LearnableWorkflowStep,
    TargetDescriptor,
    WorkflowDefinition,
    WorkflowSource,
    WorkflowStatus,
)
from app.services.workflow_memory.service import WorkflowMemoryService

logger = get_logger(__name__)


class ExplorationResult:
    """Result of exploring a website."""

    def __init__(
        self,
        pages_visited: List[PageModel],
        steps_discovered: List[LearnableWorkflowStep],
        start_url: str,
        final_url: str,
        success: bool,
        error: Optional[str] = None,
    ):
        self.pages_visited = pages_visited
        self.steps_discovered = steps_discovered
        self.start_url = start_url
        self.final_url = final_url
        self.success = success
        self.error = error


class LearningPipeline:
    """Orchestrates the explore -> learn -> store workflow.

    This pipeline is browser-agnostic. It operates on BrowserAgent
    and WorkflowMemoryService abstractions.
    """

    def __init__(
        self,
        browser: BrowserAgent,
        memory_service: WorkflowMemoryService,
        max_pages: int = 10,
        max_steps: int = 20,
        approval_callback: Optional[Any] = None,
    ):
        self._browser = browser
        self._memory = memory_service
        self._max_pages = max_pages
        self._max_steps = max_steps
        self._approval_callback = approval_callback

    async def explore_and_learn(
        self,
        url: str,
        service_id: str,
        operation: str = "new_application",
        jurisdiction_id: Optional[str] = None,
        service_name: str = "",
    ) -> WorkflowDefinition:
        """Full pipeline: explore website, learn workflow, store it.

        DISCOVER -> OBSERVE -> NORMALIZE -> UNDERSTAND -> BUILD -> VALIDATE -> STORE
        """
        logger.info("learning_pipeline_started", url=url, service_id=service_id)

        # Stage 1: DISCOVER - Open browser and navigate
        exploration = await self._discover(url)

        if not exploration.success:
            logger.error("exploration_failed", error=exploration.error)
            raise RuntimeError(f"Exploration failed: {exploration.error}")

        # Stage 2-4: OBSERVE + NORMALIZE + UNDERSTAND are done during _discover
        # The steps are already semantically described

        # Stage 5: BUILD WORKFLOW
        workflow = self._build_workflow(
            exploration=exploration,
            service_id=service_id,
            operation=operation,
            jurisdiction_id=jurisdiction_id,
            service_name=service_name,
        )

        # Stage 6: VALIDATE (basic structural validation)
        is_valid = self._validate_workflow(workflow)
        if not is_valid:
            workflow.status = WorkflowStatus.FAILED
            logger.warning("workflow_validation_failed", service_id=service_id)

        # Stage 7: STORE
        saved = await self._memory.save(workflow)
        workflow.workflow_id = str(saved.id)

        logger.info(
            "learning_pipeline_completed",
            workflow_id=str(saved.id),
            steps=len(workflow.steps),
            status=workflow.status.value,
        )

        return workflow

    async def _discover(self, url: str) -> ExplorationResult:
        """DISCOVER stage: Navigate to URL and explore the page."""
        pages_visited: List[PageModel] = []
        steps: List[LearnableWorkflowStep] = []

        try:
            # Navigate to start URL
            result = await self._browser.navigate(url)
            if not result.success:
                return ExplorationResult(
                    pages_visited=[],
                    steps_discovered=[],
                    start_url=url,
                    final_url=url,
                    success=False,
                    error=result.error,
                )

            # Inspect the page
            page = await self._browser.inspect()
            pages_visited.append(page)

            # OBSERVE + NORMALIZE + UNDERSTAND: Extract meaningful actions
            steps = self._observe_page(page, url)

        except Exception as e:
            logger.error("discovery_error", error=str(e))
            return ExplorationResult(
                pages_visited=pages_visited,
                steps_discovered=steps,
                start_url=url,
                final_url=url,
                success=False,
                error=str(e),
            )

        current_url = await self._browser.current_url()
        return ExplorationResult(
            pages_visited=pages_visited,
            steps_discovered=steps,
            start_url=url,
            final_url=current_url,
            success=True,
        )

    def _observe_page(self, page: PageModel, context_url: str) -> List[LearnableWorkflowStep]:
        """OBSERVE + NORMALIZE + UNDERSTAGE: Extract meaningful steps from a page."""
        steps: List[LearnableWorkflowStep] = []
        step_counter = 0

        for element in page.elements:
            if not element.visible or not element.enabled:
                continue

            step = self._element_to_step(element, step_counter, context_url)
            if step:
                steps.append(step)
                step_counter += 1

            if step_counter >= self._max_steps:
                break

        return steps

    def _element_to_step(
        self, element: SemanticElement, index: int, context_url: str
    ) -> Optional[LearnableWorkflowStep]:
        """Convert a semantic element to a learnable workflow step."""
        action = self._infer_action(element)
        if not action:
            return None

        target = TargetDescriptor(
            role=element.role.value if element.role else None,
            text=element.text or None,
            label=element.label or None,
            description=element.description or None,
            aria_label=element.aria_label or None,
            selector_hint=element.selector_hint or None,
            input_type=element.input_type or None,
            placeholder=element.placeholder or None,
        )

        expected = self._infer_expected_result(element, action)

        return LearnableWorkflowStep(
            step_id=f"step_{index:03d}",
            action=action,
            purpose=element.description or element.label or element.text or "",
            target_description=element.description or element.label or element.text or "",
            target=target,
            expected_result=expected,
            confidence=element.confidence,
            selector_hint=element.selector_hint,
        )

    def _infer_action(self, element: SemanticElement) -> Optional[BrowserActionType]:
        """Infer the appropriate browser action for an element."""
        role = element.role
        if role == ElementType.BUTTON:
            return BrowserActionType.CLICK
        elif role == ElementType.LINK:
            return BrowserActionType.CLICK
        elif role == ElementType.INPUT:
            if element.input_type == "file":
                return BrowserActionType.UPLOAD
            elif element.input_type in ("checkbox", "radio"):
                return BrowserActionType.CHECK
            return BrowserActionType.FILL
        elif role == ElementType.SELECT:
            return BrowserActionType.SELECT
        elif role == ElementType.TEXTAREA:
            return BrowserActionType.FILL
        elif role == ElementType.FORM:
            return None  # Forms are containers, not direct actions
        return None

    def _infer_expected_result(
        self, element: SemanticElement, action: BrowserActionType
    ) -> ExpectedResult:
        """Infer expected result after performing an action on an element."""
        if action == BrowserActionType.CLICK:
            text = (element.text or element.label or "").lower()
            if any(kw in text for kw in ["submit", "apply", "start", "next", "continue"]):
                return ExpectedResult(
                    url_changed=True,
                    description=f"Page changes after clicking {element.text or element.label}",
                )
            return ExpectedResult(
                description=f"Element responds to click: {element.text or element.label}",
            )
        elif action == BrowserActionType.FILL:
            return ExpectedResult(
                description=f"Text entered in field: {element.placeholder or element.label}",
            )
        elif action == BrowserActionType.SELECT:
            return ExpectedResult(
                description=f"Option selected from: {element.label}",
            )
        return ExpectedResult(description="Action completed")

    def _build_workflow(
        self,
        exploration: ExplorationResult,
        service_id: str,
        operation: str,
        jurisdiction_id: Optional[str],
        service_name: str,
    ) -> WorkflowDefinition:
        """BUILD WORKFLOW: Assemble exploration results into a WorkflowDefinition."""
        now = datetime.now(timezone.utc)
        version = f"{now.strftime('%Y.%m')}.1"

        return WorkflowDefinition(
            service_id=service_id,
            jurisdiction_id=jurisdiction_id,
            service_name=service_name,
            operation=operation,
            workflow_version=version,
            status=WorkflowStatus.LEARNING,
            source=WorkflowSource.EXPLORATION,
            steps=exploration.steps_discovered,
            confidence=0.5,  # Initial confidence for new workflows
            metadata={
                "start_url": exploration.start_url,
                "final_url": exploration.final_url,
                "pages_visited": len(exploration.pages_visited),
            },
        )

    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """VALIDATE: Basic structural validation of a learned workflow."""
        if not workflow.steps:
            return False
        if not workflow.service_id:
            return False
        # Check that at least one step has a reasonable confidence
        has_confident_step = any(s.confidence > 0.3 for s in workflow.steps)
        return has_confident_step
