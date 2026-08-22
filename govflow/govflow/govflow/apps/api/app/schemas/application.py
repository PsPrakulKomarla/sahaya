from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel


class ApplicationBase(BaseModel):
    service_id: UUID
    jurisdiction_id: Optional[UUID] = None
    form_data: Dict[str, Any] = {}
    document_ids: List[UUID] = []


class ApplicationCreate(ApplicationBase):
    user_id: UUID


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    reference_number: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    document_ids: Optional[List[UUID]] = None
    next_action: Optional[str] = None
    metadata_extra: Optional[Dict[str, Any]] = None


class ApplicationRead(ApplicationBase):
    id: UUID
    user_id: UUID
    status: str
    reference_number: Optional[str] = None
    submitted_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_action: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationTimelineBase(BaseModel):
    application_id: UUID
    event_type: str
    status: Optional[str] = None
    note: Optional[str] = None


class ApplicationTimelineCreate(ApplicationTimelineBase):
    pass


class ApplicationTimelineRead(ApplicationTimelineBase):
    id: UUID
    timestamp: datetime

    model_config = {"from_attributes": True}