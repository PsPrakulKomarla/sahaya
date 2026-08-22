from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class AgentTaskBase(BaseModel):
    task_type: str = "other"
    intent: Optional[str] = None
    service_query: Optional[str] = None
    service_id: Optional[UUID] = None
    jurisdiction_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    input_data: Dict[str, Any] = {}


class AgentTaskCreate(AgentTaskBase):
    user_id: UUID


class AgentTaskUpdate(BaseModel):
    status: Optional[str] = None
    current_state: Optional[str] = None
    service_id: Optional[UUID] = None
    jurisdiction_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    output_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None


class AgentTaskRead(AgentTaskBase):
    id: UUID
    user_id: UUID
    status: str
    current_state: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}