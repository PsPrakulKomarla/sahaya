from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel


class ServiceBase(BaseModel):
    service_id: str
    display_name: str
    description: str
    department: str
    jurisdiction_id: Optional[UUID] = None
    official_portal: str
    supported_languages: List[str] = ["en"]
    capabilities: List[str] = []
    required_documents: List[Dict[str, Any]] = []
    adapter: str
    workflow_version: str = "1.0.0"
    enabled: bool = True
    estimated_processing_time: Optional[str] = None
    fees: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    jurisdiction_id: Optional[UUID] = None
    official_portal: Optional[str] = None
    supported_languages: Optional[List[str]] = None
    capabilities: Optional[List[str]] = None
    required_documents: Optional[List[Dict[str, Any]]] = None
    adapter: Optional[str] = None
    workflow_version: Optional[str] = None
    enabled: Optional[bool] = None
    estimated_processing_time: Optional[str] = None
    fees: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None


class ServiceRead(ServiceBase):
    id: UUID
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}