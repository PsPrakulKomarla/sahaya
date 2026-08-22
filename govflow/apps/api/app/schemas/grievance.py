from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class GrievanceBase(BaseModel):
    service_id: UUID
    jurisdiction_id: Optional[UUID] = None
    subject: str
    description: str
    metadata_extra: Dict[str, Any] = {}


class GrievanceCreate(GrievanceBase):
    user_id: UUID
    application_id: Optional[UUID] = None


class GrievanceUpdate(BaseModel):
    status: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    official_reference_number: Optional[str] = None
    metadata_extra: Optional[Dict[str, Any]] = None


class GrievanceRead(GrievanceBase):
    id: UUID
    user_id: UUID
    application_id: Optional[UUID] = None
    status: str
    official_reference_number: Optional[str] = None
    submitted_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}