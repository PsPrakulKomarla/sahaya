import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class ServiceCapability(str):
    DISCOVER = "discover"
    ELIGIBILITY_CHECK = "eligibility_check"
    DOCUMENT_REQUIREMENTS = "document_requirements"
    NEW_APPLICATION = "new_application"
    UPDATE_RECORD = "update_record"
    RENEWAL = "renewal"
    TRACK_APPLICATION = "track_application"
    RAISE_GRIEVANCE = "raise_grievance"


class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String(255), nullable=False)
    jurisdiction_id = Column(
        UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True, index=True
    )
    official_portal = Column(String(500), nullable=False)
    supported_languages = Column(JSONB, default=["en"], nullable=False)
    capabilities = Column(JSONB, nullable=False, default=list)
    required_documents = Column(JSONB, nullable=False, default=list)
    adapter = Column(String(255), nullable=False)
    workflow_version = Column(String(50), default="1.0.0", nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    estimated_processing_time = Column(String(100), nullable=True)
    fees = Column(String(100), nullable=True)
    contact_info = Column(JSONB, default=dict, nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "service_id": self.service_id,
            "display_name": self.display_name,
            "description": self.description,
            "department": self.department,
            "jurisdiction_id": str(self.jurisdiction_id) if self.jurisdiction_id else None,
            "official_portal": self.official_portal,
            "supported_languages": self.supported_languages,
            "capabilities": self.capabilities,
            "required_documents": self.required_documents,
            "adapter": self.adapter,
            "workflow_version": self.workflow_version,
            "enabled": self.enabled,
            "estimated_processing_time": self.estimated_processing_time,
            "fees": self.fees,
            "contact_info": self.contact_info,
            "last_verified_at": self.last_verified_at.isoformat()
            if self.last_verified_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
