"""Structured error types for the agent system.

All agent errors are typed and carry structured context.
Internal stack traces are never exposed through APIs.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class AgentError(Exception):
    """Base class for all agent errors."""

    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.recoverable = recoverable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": str(self),
            "recoverable": self.recoverable,
            "details": self.details,
        }


class InvalidStateTransition(AgentError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self,
        current_state: str,
        target_state: str,
        allowed_transitions: Optional[list] = None,
    ):
        self.current_state = current_state
        self.target_state = target_state
        self.allowed_transitions = allowed_transitions or []
        super().__init__(
            message=f"Cannot transition from '{current_state}' to '{target_state}'",
            code="INVALID_STATE_TRANSITION",
            details={
                "current_state": current_state,
                "target_state": target_state,
                "allowed_transitions": self.allowed_transitions,
            },
            recoverable=False,
        )


class StepExecutionError(AgentError):
    """Raised when a workflow step fails during execution."""

    def __init__(
        self,
        step_id: str,
        step_type: str,
        reason: str,
        original_error: Optional[Exception] = None,
    ):
        self.step_id = step_id
        self.step_type = step_type
        self.original_error = original_error
        super().__init__(
            message=f"Step '{step_id}' ({step_type}) failed: {reason}",
            code="STEP_EXECUTION_ERROR",
            details={
                "step_id": step_id,
                "step_type": step_type,
                "reason": reason,
            },
            recoverable=True,
        )


class ApprovalRequired(AgentError):
    """Raised when a sensitive action requires human approval."""

    def __init__(
        self,
        action_type: str,
        reason: str,
        approval_id: Optional[str] = None,
    ):
        self.action_type = action_type
        self.approval_id = approval_id
        super().__init__(
            message=f"Action '{action_type}' requires approval: {reason}",
            code="APPROVAL_REQUIRED",
            details={
                "action_type": action_type,
                "reason": reason,
                "approval_id": approval_id,
            },
            recoverable=True,
        )


class ApprovalExpired(AgentError):
    """Raised when an approval has expired."""

    def __init__(self, approval_id: str, action_type: str):
        self.approval_id = approval_id
        self.action_type = action_type
        super().__init__(
            message=f"Approval '{approval_id}' for '{action_type}' has expired",
            code="APPROVAL_EXPIRED",
            details={"approval_id": approval_id, "action_type": action_type},
            recoverable=True,
        )


class PermissionDenied(AgentError):
    """Raised when a permission check fails."""

    def __init__(self, permission: str, context: str = ""):
        self.permission = permission
        super().__init__(
            message=f"Permission denied: {permission}" + (f" ({context})" if context else ""),
            code="PERMISSION_DENIED",
            details={"permission": permission, "context": context},
            recoverable=False,
        )


class BrowserUnavailable(AgentError):
    """Raised when the browser agent is not available."""

    def __init__(self, reason: str = "Browser agent not initialized"):
        super().__init__(
            message=reason,
            code="BROWSER_UNAVAILABLE",
            recoverable=True,
        )


class BrowserActionFailed(AgentError):
    """Raised when a browser action fails."""

    def __init__(self, action: str, reason: str, url: Optional[str] = None):
        self.action = action
        self.url = url
        super().__init__(
            message=f"Browser action '{action}' failed: {reason}",
            code="BROWSER_ACTION_FAILED",
            details={"action": action, "reason": reason, "url": url},
            recoverable=True,
        )


class TaskCancelled(AgentError):
    """Raised when an operation is attempted on a cancelled task."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(
            message=f"Task '{task_id}' has been cancelled",
            code="TASK_CANCELLED",
            details={"task_id": task_id},
            recoverable=False,
        )


class WorkflowInvalid(AgentError):
    """Raised when a workflow plan is invalid."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Invalid workflow: {reason}",
            code="WORKFLOW_INVALID",
            details=details or {},
            recoverable=False,
        )
