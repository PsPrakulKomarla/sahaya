"""Recovery type definitions — failure classification, recovery levels, decisions.

All recovery-related types are defined here as typed enums and models.
No arbitrary strings are used throughout the recovery system.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FailureType(str, Enum):
    """Typed failure categories for the recovery system."""

    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    ELEMENT_CHANGED = "ELEMENT_CHANGED"
    PAGE_CHANGED = "PAGE_CHANGED"
    NAVIGATION_FAILED = "NAVIGATION_FAILED"
    TIMEOUT = "TIMEOUT"
    UNEXPECTED_REDIRECT = "UNEXPECTED_REDIRECT"
    FORM_CHANGED = "FORM_CHANGED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    WEBSITE_UNAVAILABLE = "WEBSITE_UNAVAILABLE"
    WORKFLOW_OUTDATED = "WORKFLOW_OUTDATED"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"


class RecoveryLevel(str, Enum):
    """Layered recovery levels — from least to most aggressive.

    The engine always attempts the lowest level first.
    """

    LEVEL_1_RETRY = "LEVEL_1_RETRY"
    LEVEL_2_REINSPECT = "LEVEL_2_REINSPECT"
    LEVEL_3_SEMANTIC = "LEVEL_3_SEMANTIC"
    LEVEL_4_WORKFLOW = "LEVEL_4_WORKFLOW"
    LEVEL_5_REPLAN = "LEVEL_5_REPLAN"
    LEVEL_6_ASK_USER = "LEVEL_6_ASK_USER"
    LEVEL_7_FAIL = "LEVEL_7_FAIL"


class RecoveryDecisionType(str, Enum):
    """Possible recovery decisions."""

    RECOVER = "RECOVER"
    RETRY = "RETRY"
    VERIFY = "VERIFY"
    ASK_USER = "ASK_USER"
    ABORT = "ABORT"


class RecoveryDecision(BaseModel):
    """Structured recovery decision with confidence scoring."""

    decision: RecoveryDecisionType
    confidence: float = 0.0
    reason: str = ""
    candidate_text: Optional[str] = None
    candidate_selector: Optional[str] = None
    recovery_level: RecoveryLevel = RecoveryLevel.LEVEL_1_RETRY
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecoveryEvent(BaseModel):
    """Immutable record of a recovery event for observability."""

    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    task_id: Optional[str] = None
    step_id: Optional[str] = None
    failure_type: Optional[FailureType] = None
    recovery_level: Optional[RecoveryLevel] = None
    recovery_decision: Optional[RecoveryDecisionType] = None
    confidence: Optional[float] = None
    success: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecoveryMetrics(BaseModel):
    """Aggregated recovery metrics for observability and demo."""

    total_failures: int = 0
    total_recovery_attempts: int = 0
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    user_escalations: int = 0
    workflow_updates: int = 0
    failure_by_type: Dict[str, int] = Field(default_factory=dict)
    recovery_by_level: Dict[str, int] = Field(default_factory=dict)
    average_recovery_time_ms: float = 0.0

    @property
    def recovery_rate(self) -> float:
        """Percentage of failures that triggered recovery."""
        if self.total_failures == 0:
            return 0.0
        return self.total_recovery_attempts / self.total_failures

    @property
    def recovery_success_rate(self) -> float:
        """Percentage of recovery attempts that succeeded."""
        if self.total_recovery_attempts == 0:
            return 0.0
        return self.successful_recoveries / self.total_recovery_attempts

    @property
    def user_escalation_rate(self) -> float:
        """Percentage of failures that required user escalation."""
        if self.total_failures == 0:
            return 0.0
        return self.user_escalations / self.total_failures

    def record_failure(self, failure_type: FailureType) -> None:
        """Record a failure event."""
        self.total_failures += 1
        key = failure_type.value
        self.failure_by_type[key] = self.failure_by_type.get(key, 0) + 1

    def record_recovery_attempt(self, level: RecoveryLevel, success: bool) -> None:
        """Record a recovery attempt."""
        self.total_recovery_attempts += 1
        level_key = level.value
        self.recovery_by_level[level_key] = self.recovery_by_level.get(level_key, 0) + 1
        if success:
            self.successful_recoveries += 1
        else:
            self.failed_recoveries += 1

    def record_user_escalation(self) -> None:
        """Record a user escalation."""
        self.user_escalations += 1

    def record_workflow_update(self) -> None:
        """Record a workflow update from recovery."""
        self.workflow_updates += 1


class SafeActionClassifier:
    """Classifies whether an action is safe to retry.

    This prevents blindly retrying sensitive operations like form submission
    or payment that may have already succeeded.
    """

    SAFE_TO_RETRY = {
        "navigate",
        "inspect",
        "find_element",
        "extract",
        "scroll",
        "wait",
        "go_back",
        "screenshot",
    }

    UNSAFE_TO_RETRY = {
        "submit",
        "payment",
        "grievance_submit",
        "final_confirmation",
        "delete",
        "update_record",
    }

    @classmethod
    def is_safe_to_retry(cls, action_type: str) -> bool:
        """Check if an action type is safe to blindly retry."""
        normalized = action_type.lower().replace("-", "_")
        if normalized in cls.UNSAFE_TO_RETRY:
            return False
        if normalized in cls.SAFE_TO_RETRY:
            return True
        return False

    @classmethod
    def requires_idempotency_check(cls, action_type: str) -> bool:
        """Check if an action requires idempotency verification before retry."""
        normalized = action_type.lower().replace("-", "_")
        return normalized in cls.UNSAFE_TO_RETRY


class IdempotencyCheck(BaseModel):
    """Result of an idempotency check before retrying a sensitive action."""

    already_executed: bool = False
    evidence: str = ""
    reference_number: Optional[str] = None
    confirmation_page: bool = False
    status: str = "unknown"
    recommendation: str = "do_not_retry"


class SessionRecoveryInfo(BaseModel):
    """Information needed to recover from session failures."""

    requires_authentication: bool = False
    session_expired: bool = False
    redirect_detected: bool = False
    redirect_url: Optional[str] = None
    original_url: Optional[str] = None
    page_title: Optional[str] = None
    recommendation: str = "inspect_and_retry"
