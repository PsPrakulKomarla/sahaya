"""ApprovalService manages human approval for sensitive actions.

Responsibilities:
- Create approval requests
- Get approval status
- Approve / Reject / Expire
- Validate approval
- Prevent duplicate approval
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from packages.agent.errors import ApprovalExpired


DEFAULT_APPROVAL_TTL_MINUTES = 30


class ApprovalRequest(BaseModel):
    """An approval request for a sensitive action."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    task_id: Optional[str] = None
    action_type: str
    status: str = "pending"
    summary: str = ""
    metadata: Dict[str, dict] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    def is_valid(self) -> bool:
        return (
            self.status == "approved"
            and not self.is_expired()
        )


class ApprovalService:
    """Manages human approval for sensitive actions.

    The approval service is the single source of truth for approval state.
    It prevents duplicate approval and enforces expiration.
    """

    def __init__(
        self,
        approval_ttl_minutes: int = DEFAULT_APPROVAL_TTL_MINUTES,
    ):
        self._approvals: Dict[str, ApprovalRequest] = {}
        self._ttl_minutes = approval_ttl_minutes

    def create_approval(
        self,
        user_id: str,
        action_type: str,
        summary: str = "",
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, dict]] = None,
    ) -> ApprovalRequest:
        """Create a new approval request."""
        expires_at = datetime.utcnow() + timedelta(minutes=self._ttl_minutes)

        request = ApprovalRequest(
            user_id=user_id,
            task_id=task_id,
            action_type=action_type,
            summary=summary,
            metadata=metadata or {},
            expires_at=expires_at,
        )

        self._approvals[request.id] = request
        return request

    def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get an approval by ID."""
        return self._approvals.get(approval_id)

    def approve(self, approval_id: str) -> ApprovalRequest:
        """Approve a pending request.

        Raises:
            ApprovalExpired: If the request has expired.
            ValueError: If the request is not found or not pending.
        """
        request = self._approvals.get(approval_id)
        if request is None:
            raise ValueError(f"Approval not found: {approval_id}")

        if request.is_expired():
            request.status = "expired"
            raise ApprovalExpired(approval_id, request.action_type)

        if request.status != "pending":
            raise ValueError(f"Approval '{approval_id}' is not pending (status: {request.status})")

        request.status = "approved"
        request.approved_at = datetime.utcnow()
        return request

    def reject(self, approval_id: str) -> ApprovalRequest:
        """Reject a pending request."""
        request = self._approvals.get(approval_id)
        if request is None:
            raise ValueError(f"Approval not found: {approval_id}")

        if request.status != "pending":
            raise ValueError(f"Approval '{approval_id}' is not pending (status: {request.status})")

        request.status = "rejected"
        request.rejected_at = datetime.utcnow()
        return request

    def expire(self, approval_id: str) -> ApprovalRequest:
        """Mark an approval as expired."""
        request = self._approvals.get(approval_id)
        if request is None:
            raise ValueError(f"Approval not found: {approval_id}")

        request.status = "expired"
        return request

    def validate_approval(self, approval_id: str) -> bool:
        """Validate that an approval is current and valid."""
        request = self._approvals.get(approval_id)
        if request is None:
            return False
        return request.is_valid()

    def has_pending_approval(
        self,
        user_id: str,
        action_type: str,
        task_id: Optional[str] = None,
    ) -> Optional[ApprovalRequest]:
        """Check if there's already a pending approval for this action."""
        for request in self._approvals.values():
            if (
                request.user_id == user_id
                and request.action_type == action_type
                and request.status == "pending"
                and not request.is_expired()
            ):
                if task_id is None or request.task_id == task_id:
                    return request
        return None

    def get_user_approvals(
        self,
        user_id: str,
        status: Optional[str] = None,
    ) -> List[ApprovalRequest]:
        """Get all approvals for a user, optionally filtered by status."""
        results = [
            r for r in self._approvals.values()
            if r.user_id == user_id
        ]
        if status:
            results = [r for r in results if r.status == status]
        return results

    def generate_summary(
        self,
        action_type: str,
        service_name: str = "",
        department: str = "",
        documents: Optional[List[str]] = None,
        fields: Optional[Dict[str, str]] = None,
    ) -> str:
        """Generate a human-readable approval summary."""
        parts = [f"Action: {action_type}"]
        if service_name:
            parts.append(f"Service: {service_name}")
        if department:
            parts.append(f"Department: {department}")
        if documents:
            parts.append(f"Documents: {', '.join(documents)}")
        if fields:
            field_strs = [f"{k}: {v}" for k, v in fields.items()]
            parts.append(f"Fields: {', '.join(field_strs)}")
        return " | ".join(parts)
