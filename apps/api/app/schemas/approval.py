from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class ApprovalBase(BaseModel):
    action_type: str
    summary: Optional[str] = None
    metadata_extra: Dict[str, Any] = {}
    expires_at: Optional[datetime] = None


class ApprovalCreate(ApprovalBase):
    user_id: UUID
    task_id: Optional[UUID] = None


class ApprovalUpdate(BaseModel):
    status: Optional[str] = None


class ApprovalRead(ApprovalBase):
    id: UUID
    user_id: UUID
    task_id: Optional[UUID] = None
    status: str
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}