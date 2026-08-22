"""ExecutionContext carries all relevant context through the agent pipeline.

Step handlers, browser agents, and the safety engine receive this context.
Secrets are never stored unnecessarily.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class Permission(str, Enum):
    """Permission types for the agent system."""
    BROWSER_NAVIGATION = "BROWSER_NAVIGATION"
    READ_PAGE = "READ_PAGE"
    FILL_FORM = "FILL_FORM"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    SUBMIT_APPLICATION = "SUBMIT_APPLICATION"
    SUBMIT_GRIEVANCE = "SUBMIT_GRIEVANCE"
    MAKE_PAYMENT = "MAKE_PAYMENT"
    UPDATE_RECORD = "UPDATE_RECORD"
    DELETE_DATA = "DELETE_DATA"


# Permissions that always require approval
SENSITIVE_PERMISSIONS: Set[Permission] = {
    Permission.SUBMIT_APPLICATION,
    Permission.SUBMIT_GRIEVANCE,
    Permission.MAKE_PAYMENT,
    Permission.UPDATE_RECORD,
    Permission.DELETE_DATA,
}


class ApprovalState(BaseModel):
    """Tracks the approval status for the current context."""
    approval_id: Optional[str] = None
    action_type: Optional[str] = None
    status: Optional[str] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if the current approval is valid."""
        if not self.approval_id or self.status != "approved":
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True


class ExecutionContext(BaseModel):
    """Context passed through the agent pipeline.

    Contains task state, permissions, approval state, and metadata.
    Does NOT contain secrets or unnecessary sensitive data.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    service_id: str = ""
    jurisdiction: Dict[str, Any] = Field(default_factory=dict)
    workflow_id: Optional[str] = None
    current_step_id: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)
    approval_state: ApprovalState = Field(default_factory=ApprovalState)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def has_permission(self, permission: Permission) -> bool:
        """Check if a permission is granted."""
        return permission in self.permissions

    def requires_approval(self, permission: Permission) -> bool:
        """Check if a permission requires approval."""
        return permission in SENSITIVE_PERMISSIONS

    def grant_permission(self, permission: Permission) -> None:
        """Grant a permission."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def revoke_permission(self, permission: Permission) -> None:
        """Revoke a permission."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def set_approval(self, approval: ApprovalState) -> None:
        """Set the approval state."""
        self.approval_state = approval

    def clear_approval(self) -> None:
        """Clear the approval state."""
        self.approval_state = ApprovalState()

    def with_step(self, step_id: str) -> "ExecutionContext":
        """Return a copy with a different current step."""
        ctx = self.model_copy()
        ctx.current_step_id = step_id
        return ctx

    def summary(self) -> Dict[str, Any]:
        """Return a safe summary of the context."""
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "service_id": self.service_id,
            "current_step": self.current_step_id,
            "permissions": [p.value for p in self.permissions],
            "has_approval": self.approval_state.is_valid(),
        }
