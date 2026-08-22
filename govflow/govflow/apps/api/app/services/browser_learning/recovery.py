"""Workflow Recovery Engine - handles workflow step failures and recovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from packages.browser.interfaces.agent import BrowserAgent
from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement
from app.core.logging import get_logger
from app.services.workflow_memory.models import (
    LearnableWorkflowStep,
    TargetDescriptor,
    WorkflowDefinition,
)
from app.services.browser_learning.change_detector import PageChangeDetector, ChangeDetection

logger = get_logger(__name__)

DEFAULT_RECOVERY_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_MAX_ALTERNATIVES = 5


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""

    success: bool = False
    recovered_step: Optional[LearnableWorkflowStep] = None
    alternative_found: bool = False
    confidence: float = 0.0
    needs_human: bool = False
    reason: str = ""
    change_detection: Optional[ChangeDetection] = None


class WorkflowRecoveryEngine:
    """Handles recovery when workflow steps fail.

    The engine attempts semantic matching to find alternatives when
    expected elements are not found. If it cannot confidently determine
    the correct replacement, it stops for human assistance.
    """

    def __init__(
        self,
        browser: BrowserAgent,
        confidence_threshold: float = DEFAULT_RECOVERY_CONFIDENCE_THRESHOLD,
        max_alternatives: int = DEFAULT_MAX_ALTERNATIVES,
    ):
        self._browser = browser
        self._confidence_threshold = confidence_threshold
        self._max_alternatives = max_alternatives
        self._change_detector = PageChangeDetector()

    async def attempt_recovery(
        self,
        failed_step: LearnableWorkflowStep,
        current_page: PageModel,
        workflow: WorkflowDefinition,
    ) -> RecoveryResult:
        """Attempt to recover from a failed workflow step."""
        logger.info(
            "recovery_attempt_started",
            step_id=failed_step.step_id,
            action=failed_step.action.value,
            target=failed_step.target_description,
        )

        candidates = self._find_alternatives(failed_step, current_page)

        if not candidates:
            logger.warning("recovery_no_candidates", step_id=failed_step.step_id)
            return RecoveryResult(
                success=False,
                needs_human=True,
                reason="No matching elements found on the page",
            )

        best_candidate, best_score = self._rank_candidates(failed_step, candidates)

        if best_score < self._confidence_threshold:
            logger.warning(
                "recovery_low_confidence",
                step_id=failed_step.step_id,
                best_score=best_score,
            )
            return RecoveryResult(
                success=False,
                needs_human=True,
                confidence=best_score,
                reason=(
                    f"Best alternative confidence {best_score:.2f} "
                    f"below threshold {self._confidence_threshold}"
                ),
            )

        recovered = self._create_recovered_step(failed_step, best_candidate, best_score)

        logger.info(
            "recovery_success",
            step_id=failed_step.step_id,
            new_target=best_candidate.text or best_candidate.label,
            confidence=best_score,
        )

        return RecoveryResult(
            success=True,
            recovered_step=recovered,
            alternative_found=True,
            confidence=best_score,
        )

    async def detect_page_changes(
        self,
        expected_page: Optional[PageModel],
        actual_page: PageModel,
        expected_steps: Optional[List[LearnableWorkflowStep]] = None,
    ) -> ChangeDetection:
        """Detect changes between expected and actual page state."""
        return self._change_detector.detect(expected_page, actual_page, expected_steps)

    def _find_alternatives(
        self,
        step: LearnableWorkflowStep,
        page: PageModel,
    ) -> List[SemanticElement]:
        """Find elements that could be alternatives for the failed step."""
        candidates: List[SemanticElement] = []

        if step.target.role:
            role = None
            try:
                role = ElementType(step.target.role)
            except ValueError:
                pass
            if role:
                candidates.extend(
                    e for e in page.find_elements(role=role, visible_only=True)
                    if e not in candidates
                )

        if step.target.text:
            text_candidates = page.find_elements(text=step.target.text, visible_only=True)
            for c in text_candidates:
                if c not in candidates:
                    candidates.append(c)

        all_visible = [e for e in page.elements if e.visible and e.enabled]
        for e in all_visible:
            if e not in candidates:
                candidates.append(e)

        return candidates[: self._max_alternatives]

    def _rank_candidates(
        self,
        step: LearnableWorkflowStep,
        candidates: List[SemanticElement],
    ) -> Tuple[SemanticElement, float]:
        """Score and rank candidates by semantic similarity."""
        best: Optional[SemanticElement] = None
        best_score = 0.0

        for candidate in candidates:
            score = self._semantic_similarity(step.target, candidate)
            if score > best_score:
                best_score = score
                best = candidate

        if best is None:
            best = candidates[0] if candidates else SemanticElement()
            best_score = 0.0

        return best, best_score

    def _semantic_similarity(
        self, target: TargetDescriptor, element: SemanticElement
    ) -> float:
        """Calculate semantic similarity between a target and an element."""
        score = 0.0
        factors = 0

        if target.role:
            factors += 1
            if target.role.lower() == element.role.value.lower():
                score += 1.0

        if target.text:
            factors += 1
            score += self._text_similarity(target.text, element.text)

        if target.label:
            factors += 1
            score += self._text_similarity(target.label, element.label)

        if target.description:
            factors += 1
            score += self._text_similarity(target.description, element.description)

        if target.aria_label:
            factors += 1
            if element.aria_label:
                score += self._text_similarity(target.aria_label, element.aria_label)

        return score / factors if factors > 0 else 0.0

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using word overlap."""
        if not text1 or not text2:
            return 0.0
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        return overlap / total if total > 0 else 0.0

    def _create_recovered_step(
        self,
        original: LearnableWorkflowStep,
        alternative: SemanticElement,
        confidence: float,
    ) -> LearnableWorkflowStep:
        """Create a new step based on the recovered alternative."""
        return LearnableWorkflowStep(
            step_id=f"{original.step_id}_recovered",
            action=original.action,
            purpose=original.purpose,
            target_description=(
                f"Recovered: {alternative.text or alternative.label or original.target_description}"
            ),
            target=TargetDescriptor(
                role=alternative.role.value if alternative.role else original.target.role,
                text=alternative.text or original.target.text,
                label=alternative.label or original.target.label,
                description=alternative.description or original.target.description,
                aria_label=alternative.aria_label or original.target.aria_label,
                selector_hint=alternative.selector_hint or original.target.selector_hint,
            ),
            expected_result=original.expected_result,
            confidence=confidence,
            optional=original.optional,
            requires_human_approval=original.requires_human_approval,
            retry_policy=original.retry_policy,
            metadata={"recovered_from": original.step_id, "original_target": original.target_description},
        )
