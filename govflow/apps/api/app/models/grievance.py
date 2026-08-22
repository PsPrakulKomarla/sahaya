import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class GrievanceStatus(str):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    AWAITING_APPROVAL = "awaiting_approval"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True)
    status = Column(String(30), default=GrievanceStatus.DRAFT, nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    official_reference_number = Column(String(100), nullable=True, index=True)
    metadata_extra = Column(JSONB, default=dict, nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "application_id": str(self.application_id) if self.application_id else None,
            "service_id": str(self.service_id),
            "jurisdiction_id": str(self.jurisdiction_id) if self.jurisdiction_id else None,
            "status": self.status,
            "subject": self.subject,
            "description": self.description,
            "official_reference_number": self.official_reference_number,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
