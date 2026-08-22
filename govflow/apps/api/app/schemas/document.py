from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class DocumentBase(BaseModel):
    document_type: str
    file_name: str
    storage_reference: str
    mime_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    user_id: UUID


class DocumentUpdate(BaseModel):
    verification_status: Optional[str] = None
    ocr_status: Optional[str] = None
    ocr_confidence: Optional[float] = None
    extracted_data: Optional[Dict[str, Any]] = None
    extracted_data_ref: Optional[str] = None
    expires_at: Optional[datetime] = None


class DocumentRead(DocumentBase):
    id: UUID
    user_id: UUID
    verification_status: str
    ocr_status: str
    ocr_confidence: Optional[float] = None
    extracted_data: Optional[Dict[str, Any]] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}