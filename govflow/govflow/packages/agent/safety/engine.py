"""SafetyPolicyEngine evaluates every sensitive action before execution.

The engine is centralized — approval logic is NOT implemented separately
in each adapter or step handler.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, Field

from packages.agent.executor.context import Permission, SENSITIVE_PERMISSIONS

logger = logging.getLogger(__name__)


class SafetyDecisionType(str, Enum):
    """Possible safety decisions."""
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"
    ASK_USER = "ASK_USER"


class SafetyDecision(BaseModel):
    """Result of a safety evaluation."""
    decision: SafetyDecisionType
    reason: str
    action_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Actions that always require approval regardless of context
ALWAYS_SENSITIVE: Set[str] = {
    "SUBMIT_APPLICATION",
    "SUBMIT_GRIEVANCE",
    "MAKE_PAYMENT",
    "UPDATE_RECORD",
    "DELETE_DATA",
    "SEND_MESSAGE",
    "FINAL_CONFIRMATION",
}

# Actions that are always denied in the current phase
ALWAYS_DENIED: Set[str] = set()


class SafetyPolicyEngine:
    """Evaluates every sensitive action before execution.

    The safety engine is the single point of control for action authorization.
    All sensitive actions must pass through this engine.
    """

    def __init__(
        self,
        additional_sensitive: Optional[Set[str]] = None,
        additional_denied: Optional[Set[str]] = None,
    ):
        self._sensitive_actions = ALWAYS_SENSITIVE.copy()
        if additional_sensitive:
            self._sensitive_actions.update(additional_sensitive)

        self._denied_actions = ALWAYS_DENIED.copy()
        if additional_denied:
            self._denied_actions.update(additional_denied)

    def evaluate(
        self,
        action_type: str,
        has_approval: bool = False,
        approval_valid: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> SafetyDecision:
        """Evaluate whether an action should be allowed.

        Args:
            action_type: The type of action being attempted.
            has_approval: Whether an approval exists for this action.
            approval_valid: Whether the existing approval is still valid.
            context: Additional context for the evaluation.

        Returns:
            A SafetyDecision indicating whether to allow, require approval,
            deny, or ask the user.
        """
        if action_type in self._denied_actions:
            logger.warning("Action denied by policy: %s", action_type)
            return SafetyDecision(
                decision=SafetyDecisionType.DENY,
                reason=f"Action '{action_type}' is not permitted by policy",
                action_type=action_type,
            )

        if action_type in self._sensitive_actions:
            if has_approval and approval_valid:
                logger.info("Action approved: %s", action_type)
                return SafetyDecision(
                    decision=SafetyDecisionType.ALLOW,
                    reason=f"Valid approval exists for '{action_type}'",
                    action_type=action_type,
                )
            else:
                logger.info("Action requires approval: %s", action_type)
                return SafetyDecision(
                    decision=SafetyDecisionType.REQUIRE_APPROVAL,
                    reason=f"Action '{action_type}' requires explicit user approval",
                    action_type=action_type,
                )

        return SafetyDecision(
            decision=SafetyDecisionType.ALLOW,
            reason=f"Action '{action_type}' is not classified as sensitive",
            action_type=action_type,
        )

    def is_sensitive(self, action_type: str) -> bool:
        """Check if an action is classified as sensitive."""
        return action_type in self._sensitive_actions

    def register_sensitive(self, action_type: str) -> None:
        """Register a new action type as sensitive."""
        self._sensitive_actions.add(action_type)

    def register_denied(self, action_type: str) -> None:
        """Register a new action type as denied."""
        self._denied_actions.add(action_type)

    def get_sensitive_actions(self) -> Set[str]:
        """Get all sensitive action types."""
        return self._sensitive_actions.copy()

    def get_denied_actions(self) -> Set[str]:
        """Get all denied action types."""
        return self._denied_actions.copy()
