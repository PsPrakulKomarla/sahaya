"""RecoveryEngine — layered recovery for browser agent failures.

Implements 7 recovery levels from simple retry to safe failure.
Prevents infinite recovery loops and enforces idempotency for sensitive actions.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from packages.agent.recovery.types import (
    FailureType,
    RecoveryDecision,
    RecoveryDecisionType,
    RecoveryEvent,
    RecoveryLevel,
    RecoveryMetrics,
    SafeActionClassifier,
    SessionRecoveryInfo,
)
from packages.browser.interfaces.agent import BrowserAgent
from packages.browser.interfaces.models import ElementType, PageModel, SemanticElement
from packages.agent.planner.models import WorkflowPlan, WorkflowStep, StepStatus

DEFAULT_MAX_STEP_RECOVERY_ATTEMPTS = 3
DEFAULT_MAX_WORKFLOW_RECOVERY_ATTEMPTS = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_RETRY_DELAY_SECONDS = 0.1
DEFAULT_RETRY_BACKOFF = 2.0
MAX_RETRY_DELAY_SECONDS = 30.0


class RecoveryConfiguration:
    def __init__(
        self,
        max_step_recovery_attempts: int = DEFAULT_MAX_STEP_RECOVERY_ATTEMPTS,
        max_workflow_recovery_attempts: int = DEFAULT_MAX_WORKFLOW_RECOVERY_ATTEMPTS,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
    ):
        self.max_step_recovery_attempts = max_step_recovery_attempts
        self.max_workflow_recovery_attempts = max_workflow_recovery_attempts
        self.confidence_threshold = confidence_threshold
        self.retry_delay_seconds = retry_delay_seconds
        self.retry_backoff = retry_backoff


class RecoveryEngine:
    def __init__(
        self,
        browser: Optional[BrowserAgent] = None,
        config: Optional[RecoveryConfiguration] = None,
    ):
        self._browser = browser
        self._config = config or RecoveryConfiguration()
        self._metrics = RecoveryMetrics()
        self._events: List[RecoveryEvent] = []
        self._step_attempts: Dict[str, int] = {}
        self._workflow_attempts: int = 0

    @property
    def metrics(self) -> RecoveryMetrics:
        return self._metrics

    @property
    def events(self) -> List[RecoveryEvent]:
        return list(self._events)

    async def handle_failure(
        self,
        failed_step: WorkflowStep,
        error: Exception,
        current_page: Optional[PageModel] = None,
        plan: Optional[WorkflowPlan] = None,
    ) -> RecoveryDecision:
        failure_type = self._classify_failure(error, current_page)
        self._metrics.record_failure(failure_type)

        step_id = failed_step.id or "unknown"
        step_count = self._step_attempts.get(step_id, 0)
        workflow_count = self._workflow_attempts

        self._record_event(
            event_type="failure_detected",
            step_id=step_id,
            failure_type=failure_type,
            recovery_level=None,
            recovery_decision=None,
            confidence=0.0,
            success=False,
            metadata={"error": str(error)},
        )

        if failure_type in (
            FailureType.SESSION_EXPIRED,
            FailureType.AUTHENTICATION_REQUIRED,
            FailureType.WEBSITE_UNAVAILABLE,
        ):
            self._metrics.record_user_escalation()
            decision = RecoveryDecision(
                decision=RecoveryDecisionType.ASK_USER,
                confidence=1.0,
                reason=failure_type.value,
                recovery_level=RecoveryLevel.LEVEL_6_ASK_USER,
                metadata={"error": str(error)},
            )
            self._record_event(
                event_type="recovery_decision",
                step_id=step_id,
                failure_type=failure_type,
                recovery_level=RecoveryLevel.LEVEL_6_ASK_USER,
                recovery_decision=RecoveryDecisionType.ASK_USER,
                confidence=1.0,
                success=False,
            )
            return decision

        if step_count >= self._config.max_step_recovery_attempts:
            self._metrics.record_user_escalation()
            return RecoveryDecision(
                decision=RecoveryDecisionType.ASK_USER,
                confidence=0.0,
                reason="max_step_recovery_attempts_exceeded",
                recovery_level=RecoveryLevel.LEVEL_6_ASK_USER,
                metadata={"step_id": step_id, "attempts": step_count},
            )

        if workflow_count >= self._config.max_workflow_recovery_attempts:
            self._metrics.record_user_escalation()
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="max_workflow_recovery_attempts_exceeded",
                recovery_level=RecoveryLevel.LEVEL_7_FAIL,
                metadata={"workflow_attempts": workflow_count},
            )

        self._step_attempts[step_id] = step_count + 1
        self._workflow_attempts += 1

        decision = await self._attempt_layered_recovery(
            failed_step, failure_type, current_page, plan
        )

        success = decision.decision in (
            RecoveryDecisionType.RECOVER,
            RecoveryDecisionType.RETRY,
            RecoveryDecisionType.VERIFY,
        )
        self._metrics.record_recovery_attempt(decision.recovery_level, success)

        self._record_event(
            event_type="recovery_decision",
            step_id=step_id,
            failure_type=failure_type,
            recovery_level=decision.recovery_level,
            recovery_decision=decision.decision,
            confidence=decision.confidence,
            success=success,
            metadata=decision.metadata,
        )

        return decision

    async def attempt_recovery(
        self,
        failed_step: WorkflowStep,
        current_page: Optional[PageModel] = None,
        plan: Optional[WorkflowPlan] = None,
        error: Optional[Exception] = None,
    ) -> RecoveryDecision:
        if error is None:
            error = Exception("unknown_error")
        return await self.handle_failure(failed_step, error, current_page, plan)

    def _classify_failure(self, error: Exception, current_page: Optional[PageModel] = None) -> FailureType:
        msg = str(error).lower()
        err_type = type(error).__name__.lower()

        if "session" in msg and ("expired" in msg or "timed out" in msg):
            return FailureType.SESSION_EXPIRED
        if "auth" in msg or "login" in msg or "unauthorized" in msg:
            return FailureType.AUTHENTICATION_REQUIRED
        if "unavailable" in msg or "503" in msg or "502" in msg or "connection refused" in msg:
            return FailureType.WEBSITE_UNAVAILABLE
        if "timeout" in msg or "timed out" in msg or "timeouterror" in err_type:
            return FailureType.TIMEOUT
        if "element not found" in msg or "nosuchelement" in err_type or "no element" in msg:
            return FailureType.ELEMENT_NOT_FOUND
        if "element changed" in msg or "stale element" in msg or "staleelement" in err_type:
            return FailureType.ELEMENT_CHANGED
        if "page changed" in msg or "page not loaded" in msg:
            return FailureType.PAGE_CHANGED
        if "navigation" in msg and ("fail" in msg or "error" in msg):
            return FailureType.NAVIGATION_FAILED
        if "redirect" in msg:
            return FailureType.UNEXPECTED_REDIRECT
        if "form" in msg and ("changed" in msg or "missing" in msg):
            return FailureType.FORM_CHANGED
        if "validat" in msg:
            return FailureType.VALIDATION_ERROR
        if "outdated" in msg or "mismatch" in msg or "workflow" in msg:
            return FailureType.WORKFLOW_OUTDATED

        if current_page is not None:
            title = current_page.title.lower()
            if "login" in title or "sign in" in title:
                return FailureType.AUTHENTICATION_REQUIRED
            if "session" in title or "expired" in title:
                return FailureType.SESSION_EXPIRED

        return FailureType.UNKNOWN_FAILURE

    async def _attempt_layered_recovery(
        self,
        failed_step: WorkflowStep,
        failure_type: FailureType,
        current_page: Optional[PageModel],
        plan: Optional[WorkflowPlan],
    ) -> RecoveryDecision:
        element_failures = {
            FailureType.ELEMENT_NOT_FOUND,
            FailureType.ELEMENT_CHANGED,
            FailureType.FORM_CHANGED,
        }

        if failure_type in element_failures:
            decision = await self._level_2_reinspect(failed_step, current_page)
            if decision.decision != RecoveryDecisionType.ABORT:
                return decision

            decision = await self._level_3_semantic(failed_step, current_page)
            if decision.decision != RecoveryDecisionType.ABORT:
                return decision

        if failure_type == FailureType.WORKFLOW_OUTDATED:
            decision = await self._level_4_workflow_compare(failed_step, plan)
            if decision.decision != RecoveryDecisionType.ABORT:
                return decision

        if failure_type in {FailureType.PAGE_CHANGED, FailureType.UNEXPECTED_REDIRECT, FailureType.NAVIGATION_FAILED}:
            decision = await self._level_5_replan(failed_step, plan)
            if decision.decision != RecoveryDecisionType.ABORT:
                return decision

        decision = await self._level_1_retry(failed_step)
        if decision.decision != RecoveryDecisionType.ABORT:
            return decision

        return RecoveryDecision(
            decision=RecoveryDecisionType.ABORT,
            confidence=0.0,
            reason="all_recovery_levels_exhausted",
            recovery_level=RecoveryLevel.LEVEL_7_FAIL,
        )

    async def _level_1_retry(self, step: WorkflowStep) -> RecoveryDecision:
        action_type = step.input_data.get("action_type", "unknown")
        if not SafeActionClassifier.is_safe_to_retry(action_type):
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="unsafe_action",
                recovery_level=RecoveryLevel.LEVEL_1_RETRY,
            )

        delay = self._config.retry_delay_seconds
        await asyncio.sleep(delay)

        return RecoveryDecision(
            decision=RecoveryDecisionType.RETRY,
            confidence=0.5,
            reason="retry_after_delay",
            recovery_level=RecoveryLevel.LEVEL_1_RETRY,
            metadata={"delay_seconds": delay},
        )

    async def _level_2_reinspect(
        self, step: WorkflowStep, current_page: Optional[PageModel]
    ) -> RecoveryDecision:
        if self._browser is None or current_page is None:
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="no_browser_or_page",
                recovery_level=RecoveryLevel.LEVEL_2_REINSPECT,
            )

        target_text = step.input_data.get("target_text", "")
        target_role_str = step.input_data.get("target_role", "")
        target_role = None
        if target_role_str:
            try:
                target_role = ElementType(target_role_str)
            except ValueError:
                pass

        if target_role is not None:
            found = current_page.find_element(role=target_role, text=target_text, visible_only=True)
        elif target_text:
            found = current_page.find_element(text=target_text, visible_only=True)
        else:
            found = None

        if found is not None:
            return RecoveryDecision(
                decision=RecoveryDecisionType.RECOVER,
                confidence=found.confidence,
                reason="element_found_on_reinspect",
                candidate_text=found.text,
                candidate_selector=found.selector_hint,
                recovery_level=RecoveryLevel.LEVEL_2_REINSPECT,
            )

        try:
            fresh_page = await self._browser.inspect()
            if target_role is not None:
                found = fresh_page.find_element(role=target_role, text=target_text, visible_only=True)
            elif target_text:
                found = fresh_page.find_element(text=target_text, visible_only=True)
            else:
                found = None

            if found is not None:
                return RecoveryDecision(
                    decision=RecoveryDecisionType.RECOVER,
                    confidence=found.confidence,
                    reason="element_found_after_reinspect",
                    candidate_text=found.text,
                    candidate_selector=found.selector_hint,
                    recovery_level=RecoveryLevel.LEVEL_2_REINSPECT,
                )
        except Exception:
            pass

        return RecoveryDecision(
            decision=RecoveryDecisionType.ABORT,
            confidence=0.0,
            reason="element_not_found_on_reinspect",
            recovery_level=RecoveryLevel.LEVEL_2_REINSPECT,
        )

    async def _level_3_semantic(
        self, step: WorkflowStep, current_page: Optional[PageModel]
    ) -> RecoveryDecision:
        if current_page is None:
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="no_page_for_semantic_search",
                recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
            )

        target_text = step.input_data.get("target_text", "")
        target_role_str = step.input_data.get("target_role", "")
        target_role = None
        if target_role_str:
            try:
                target_role = ElementType(target_role_str)
            except ValueError:
                pass

        candidates = self._find_semantic_candidates(current_page, target_text, target_role)

        if not candidates:
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="no_semantic_candidates",
                recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
            )

        best_element, best_score = self._rank_semantic_candidates(target_text, candidates)

        if best_score >= self._config.confidence_threshold:
            return RecoveryDecision(
                decision=RecoveryDecisionType.RECOVER,
                confidence=best_score,
                reason="semantic_match_found",
                candidate_text=best_element.text,
                candidate_selector=best_element.selector_hint,
                recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
                metadata={"all_scores": [s for _, s in candidates]},
            )

        return RecoveryDecision(
            decision=RecoveryDecisionType.ABORT,
            confidence=best_score,
            reason="semantic_confidence_below_threshold",
            recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
        )

    async def _level_4_workflow_compare(
        self, step: WorkflowStep, plan: Optional[WorkflowPlan]
    ) -> RecoveryDecision:
        if plan is None:
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="no_plan_for_comparison",
                recovery_level=RecoveryLevel.LEVEL_4_WORKFLOW,
            )

        for plan_step in plan.steps:
            if plan_step.id == step.id:
                continue
            if plan_step.status != StepStatus.COMPLETED:
                continue
            if plan_step.description == step.description:
                self._metrics.record_workflow_update()
                return RecoveryDecision(
                    decision=RecoveryDecisionType.RECOVER,
                    confidence=0.8,
                    reason="workflow_step_already_completed",
                    recovery_level=RecoveryLevel.LEVEL_4_WORKFLOW,
                    metadata={"matching_step_id": plan_step.id},
                )

        self._metrics.record_workflow_update()
        return RecoveryDecision(
            decision=RecoveryDecisionType.RETRY,
            confidence=0.4,
            reason="workflow_plan_outdated_retry",
            recovery_level=RecoveryLevel.LEVEL_4_WORKFLOW,
        )

    async def _level_5_replan(
        self, step: WorkflowStep, plan: Optional[WorkflowPlan]
    ) -> RecoveryDecision:
        if plan is None:
            return RecoveryDecision(
                decision=RecoveryDecisionType.ABORT,
                confidence=0.0,
                reason="no_plan_for_replan",
                recovery_level=RecoveryLevel.LEVEL_5_REPLAN,
            )

        current_page_url = ""
        if self._browser is not None:
            try:
                current_page_url = await self._browser.current_url()
            except Exception:
                pass

        if current_page_url:
            for plan_step in plan.steps:
                expected_url = plan_step.input_data.get("url", "")
                if expected_url and expected_url != current_page_url:
                    self._metrics.record_workflow_update()
                    return RecoveryDecision(
                        decision=RecoveryDecisionType.RETRY,
                        confidence=0.6,
                        reason="replan_navigate_to_expected_url",
                        recovery_level=RecoveryLevel.LEVEL_5_REPLAN,
                        metadata={
                            "current_url": current_page_url,
                            "expected_url": expected_url,
                        },
                    )

        self._metrics.record_workflow_update()
        return RecoveryDecision(
            decision=RecoveryDecisionType.ASK_USER,
            confidence=0.3,
            reason="replan_cannot_determine_fix",
            recovery_level=RecoveryLevel.LEVEL_5_REPLAN,
        )

    def _find_semantic_candidates(
        self, page: PageModel, target_text: str, target_role: Optional[ElementType]
    ) -> List[Tuple[SemanticElement, float]]:
        candidates: List[Tuple[SemanticElement, float]] = []

        for element in page.elements:
            if not element.visible:
                continue
            if target_role is not None and element.role != target_role:
                continue
            score = self._text_similarity(target_text, element.text)
            candidates.append((element, score))

        return candidates

    def _rank_semantic_candidates(
        self, target_text: str, candidates: List[Tuple[SemanticElement, float]]
    ) -> Tuple[SemanticElement, float]:
        if not candidates:
            raise ValueError("no candidates to rank")

        scored: List[Tuple[SemanticElement, float]] = []
        for element, base_score in candidates:
            bonus = 0.0
            if element.text.lower().strip() == target_text.lower().strip():
                bonus = 0.3
            elif target_text.lower().strip() in element.text.lower():
                bonus = 0.15
            scored.append((element, min(base_score + bonus, 1.0)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0]

    def _text_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0

    def _record_event(
        self,
        event_type: str,
        step_id: Optional[str] = None,
        failure_type: Optional[FailureType] = None,
        recovery_level: Optional[RecoveryLevel] = None,
        recovery_decision: Optional[RecoveryDecisionType] = None,
        confidence: float = 0.0,
        success: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RecoveryEvent:
        event = RecoveryEvent(
            event_type=event_type,
            step_id=step_id,
            failure_type=failure_type,
            recovery_level=recovery_level,
            recovery_decision=recovery_decision,
            confidence=confidence,
            success=success,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def reset_step_attempts(self, step_id: str) -> None:
        self._step_attempts.pop(step_id, None)

    def reset_workflow_attempts(self) -> None:
        self._workflow_attempts = 0

    def get_step_attempts(self, step_id: str) -> int:
        return self._step_attempts.get(step_id, 0)


def classify_failure_from_page(expected_page: str, actual_page: str) -> FailureType:
    if expected_page == actual_page:
        return FailureType.UNKNOWN_FAILURE

    actual_lower = actual_page.lower()
    if "login" in actual_lower or "sign in" in actual_lower:
        return FailureType.AUTHENTICATION_REQUIRED
    if "session" in actual_lower or "expired" in actual_lower:
        return FailureType.SESSION_EXPIRED
    if "unavailable" in actual_lower or "error" in actual_lower:
        return FailureType.WEBSITE_UNAVAILABLE

    return FailureType.UNEXPECTED_REDIRECT


def create_safe_retry_wrapper(engine: RecoveryEngine, step: WorkflowStep) -> Callable:
    async def wrapper(func: Callable, *args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            current_page = None
            if engine._browser is not None:
                try:
                    current_page = await engine._browser.inspect()
                except Exception:
                    pass

            decision = await engine.handle_failure(step, exc, current_page)

            if decision.decision in (
                RecoveryDecisionType.RECOVER,
                RecoveryDecisionType.RETRY,
                RecoveryDecisionType.VERIFY,
            ):
                return await func(*args, **kwargs)

            raise
