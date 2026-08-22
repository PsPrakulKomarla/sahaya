from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class WorkflowBase(BaseModel):
    service_id: UUID
    jurisdiction_id: Optional[UUID] = None
    workflow_version: str
    workflow_definition: Dict[str, Any] = {}
    confidence: Optional[float] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    workflow_version: Optional[str] = None
    status: Optional[str] = None
    workflow_definition: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None


class WorkflowRead(WorkflowBase):
    id: UUID
    status: str
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}