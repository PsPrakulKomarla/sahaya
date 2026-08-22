from enum import Enum
from typing import Optional, List, Set
from packages.agent.models.tasks import StepType


class SafetyDecision(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"
    ASK_USER = "ASK_USER"


SENSITIVE_ACTIONS: Set[StepType] = {
    StepType.SUBMIT,
    StepType.UPDATE_RECORD,
    StepType.RENEW,
    StepType.RAISE_GRIEVANCE,
}


class SafetyPolicyEngine:
    """Evaluates every sensitive action before execution."""

    def __init__(self, extra_sensitive: Optional[Set[StepType]] = None):
        self._sensitive = SENSITIVE_ACTIONS.copy()
        if extra_sensitive:
            self._sensitive.update(extra_sensitive)
        self._denied_actions: Set[StepType] = set()

    def evaluate(self, step_type: StepType, context: dict = None) -> SafetyDecision:
        if step_type in self._denied_actions:
            return SafetyDecision.DENY

        if step_type not in self._sensitive:
            return SafetyDecision.ALLOW

        context = context or {}
        has_approval = context.get("has_approval", False)
        approval_valid = context.get("approval_valid", False)

        if has_approval and approval_valid:
            return SafetyDecision.ALLOW

        return SafetyDecision.REQUIRE_APPROVAL

    def deny_action(self, step_type: StepType) -> None:
        self._denied_actions.add(step_type)

    def allow_action(self, step_type: StepType) -> None:
        self._denied_actions.discard(step_type)

    def is_sensitive(self, step_type: StepType) -> bool:
        return step_type in self._sensitive
