from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class AuditEventBase(BaseModel):
    event_type: str
    metadata_redacted: Dict[str, Any] = {}


class AuditEventCreate(AuditEventBase):
    user_id: Optional[UUID] = None
    task_id: Optional[UUID] = None


class AuditEventRead(AuditEventBase):
    id: UUID
    user_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    timestamp: datetime

    model_config = {"from_attributes": True}