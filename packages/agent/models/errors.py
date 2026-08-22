from typing import Optional, Any


class AgentError(Exception):
    """Base error for agent operations."""
    def __init__(self, message: str, code: str, recoverable: bool = True, details: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.recoverable = recoverable
        self.details = details


class InvalidStateTransition(AgentError):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            f"Invalid transition from {from_state} to {to_state}",
            code="INVALID_STATE_TRANSITION",
            recoverable=False,
            details={"from_state": from_state, "to_state": to_state},
        )


class StepExecutionError(AgentError):
    """Raised when a step fails to execute."""
    def __init__(self, step_id: str, step_type: str, reason: str):
        super().__init__(
            f"Step {step_id} ({step_type}) failed: {reason}",
            code="STEP_EXECUTION_ERROR",
            recoverable=True,
            details={"step_id": step_id, "step_type": step_type, "reason": reason},
        )


class ApprovalRequired(AgentError):
    """Raised when an action requires human approval."""
    def __init__(self, action: str, summary: str = ""):
        super().__init__(
            f"Approval required for: {action}",
            code="APPROVAL_REQUIRED",
            recoverable=True,
            details={"action": action, "summary": summary},
        )


class ApprovalExpired(AgentError):
    """Raised when an approval has expired."""
    def __init__(self, approval_id: str):
        super().__init__(
            f"Approval {approval_id} has expired",
            code="APPROVAL_EXPIRED",
            recoverable=True,
            details={"approval_id": approval_id},
        )


class PermissionDenied(AgentError):
    """Raised when a permission check fails."""
    def __init__(self, permission: str, action: str = ""):
        super().__init__(
            f"Permission denied: {permission}" + (f" for {action}" if action else ""),
            code="PERMISSION_DENIED",
            recoverable=False,
            details={"permission": permission, "action": action},
        )


class BrowserUnavailable(AgentError):
    """Raised when the browser agent is not available."""
    def __init__(self, reason: str = "Browser agent not initialized"):
        super().__init__(
            reason,
            code="BROWSER_UNAVAILABLE",
            recoverable=True,
        )


class BrowserActionFailed(AgentError):
    """Raised when a browser action fails."""
    def __init__(self, action: str, reason: str, url: Optional[str] = None):
        super().__init__(
            f"Browser action '{action}' failed: {reason}",
            code="BROWSER_ACTION_FAILED",
            recoverable=True,
            details={"action": action, "reason": reason, "url": url},
        )


class TaskCancelled(AgentError):
    """Raised when trying to operate on a cancelled task."""
    def __init__(self, task_id: str):
        super().__init__(
            f"Task {task_id} has been cancelled",
            code="TASK_CANCELLED",
            recoverable=False,
            details={"task_id": task_id},
        )


class WorkflowInvalid(AgentError):
    """Raised when a workflow plan is invalid."""
    def __init__(self, reason: str):
        super().__init__(
            f"Invalid workflow: {reason}",
            code="WORKFLOW_INVALID",
            recoverable=False,
            details={"reason": reason},
        )
