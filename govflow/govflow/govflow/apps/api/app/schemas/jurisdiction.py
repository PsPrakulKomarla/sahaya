from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class JurisdictionBase(BaseModel):
    code: str
    name: str
    country: str
    state: str
    district: Optional[str] = None
    municipality: Optional[str] = None
    parent_id: Optional[UUID] = None


class JurisdictionCreate(JurisdictionBase):
    pass


class JurisdictionUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    municipality: Optional[str] = None
    is_active: Optional[bool] = None


class JurisdictionRead(JurisdictionBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}