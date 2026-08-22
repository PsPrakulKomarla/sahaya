from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import uuid


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalType(str, Enum):
    SUBMIT_APPLICATION = "SUBMIT_APPLICATION"
    SUBMIT_GRIEVANCE = "SUBMIT_GRIEVANCE"
    MAKE_PAYMENT = "MAKE_PAYMENT"
    UPDATE_RECORD = "UPDATE_RECORD"
    DELETE_DATA = "DELETE_DATA"
    OTHER = "OTHER"


class Approval:
    def __init__(
        self,
        approval_id: str,
        action_type: str,
        status: ApprovalStatus,
        summary: Dict[str, Any],
        expires_at: datetime,
        user_id: str,
        task_id: str,
    ):
        self.approval_id = approval_id
        self.action_type = action_type
        self.status = status
        self.summary = summary
        self.expires_at = expires_at
        self.user_id = user_id
        self.task_id = task_id
        self.created_at = datetime.utcnow()
        self.approved_at: Optional[datetime] = None
        self.rejected_at: Optional[datetime] = None


class ApprovalService:
    """Manages human approval workflow."""

    def __init__(self, approval_ttl_minutes: int = 30):
        self._approvals: Dict[str, Approval] = {}
        self._approval_ttl = timedelta(minutes=approval_ttl_minutes)

    def create_approval(
        self,
        action_type: str,
        summary: Dict[str, Any],
        user_id: str,
        task_id: str,
    ) -> Approval:
        approval_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + self._approval_ttl

        approval = Approval(
            approval_id=approval_id,
            action_type=action_type,
            status=ApprovalStatus.PENDING,
            summary=summary,
            expires_at=expires_at,
            user_id=user_id,
            task_id=task_id,
        )
        self._approvals[approval_id] = approval
        return approval

    def get_approval(self, approval_id: str) -> Optional[Approval]:
        approval = self._approvals.get(approval_id)
        if approval and approval.status == ApprovalStatus.PENDING:
            if datetime.utcnow() > approval.expires_at:
                approval.status = ApprovalStatus.EXPIRED
        return approval

    def approve(self, approval_id: str) -> Optional[Approval]:
        approval = self.get_approval(approval_id)
        if approval is None or approval.status != ApprovalStatus.PENDING:
            return None
        if datetime.utcnow() > approval.expires_at:
            approval.status = ApprovalStatus.EXPIRED
            return None
        approval.status = ApprovalStatus.APPROVED
        approval.approved_at = datetime.utcnow()
        return approval

    def reject(self, approval_id: str) -> Optional[Approval]:
        approval = self.get_approval(approval_id)
        if approval is None or approval.status != ApprovalStatus.PENDING:
            return None
        approval.status = ApprovalStatus.REJECTED
        approval.rejected_at = datetime.utcnow()
        return approval

    def validate_approval(self, approval_id: str) -> bool:
        approval = self.get_approval(approval_id)
        if approval is None:
            return False
        if approval.status == ApprovalStatus.EXPIRED:
            return False
        if approval.status != ApprovalStatus.APPROVED:
            return False
        if datetime.utcnow() > approval.expires_at:
            approval.status = ApprovalStatus.EXPIRED
            return False
        return True

    def has_pending_approval(self, task_id: str, action_type: str) -> bool:
        for approval in self._approvals.values():
            if (
                approval.task_id == task_id
                and approval.action_type == action_type
                and approval.status == ApprovalStatus.PENDING
                and datetime.utcnow() <= approval.expires_at
            ):
                return True
        return False
