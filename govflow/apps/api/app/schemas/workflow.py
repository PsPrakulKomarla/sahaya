from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class WorkflowBase(BaseModel):
    service_id: UUID
    jurisdiction_id: Optional[UUID] = None
    workflow_version: str
    workflow_definition: Dict[str, Any] = {}
    confidence: Optional[float] = None
    source: str = "exploration"


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    workflow_version: Optional[str] = None
    status: Optional[str] = None
    workflow_definition: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    source: Optional[str] = None


class WorkflowRead(WorkflowBase):
    id: UUID
    status: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    recovery_count: int = 0
    last_verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowStatusResponse(BaseModel):
    workflow_id: UUID
    status: str
    confidence: Optional[float] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    recovery_count: int = 0
    last_verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class WorkflowExploreRequest(BaseModel):
    service_id: UUID
    jurisdiction_id: Optional[UUID] = None
    url: str
    operation: str = "new_application"


class WorkflowExploreResponse(BaseModel):
    task_id: str
    status: str
    message: str


class WorkflowInvalidateRequest(BaseModel):
    reason: str = ""
