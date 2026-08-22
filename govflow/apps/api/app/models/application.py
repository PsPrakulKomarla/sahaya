import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class ApplicationStatus(str):
    DRAFT = "draft"
    REQUIREMENTS_PENDING = "requirements_pending"
    READY_FOR_REVIEW = "ready_for_review"
    AWAITING_APPROVAL = "awaiting_approval"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    ACTION_REQUIRED = "action_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True)
    status = Column(String(30), default=ApplicationStatus.DRAFT, nullable=False, index=True)
    reference_number = Column(String(100), nullable=True, index=True)
    form_data = Column(JSONB, default=dict, nullable=False)
    document_ids = Column(JSONB, default=list, nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    next_action = Column(String(255), nullable=True)
    metadata_extra = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "service_id": str(self.service_id),
            "jurisdiction_id": str(self.jurisdiction_id) if self.jurisdiction_id else None,
            "status": self.status,
            "reference_number": self.reference_number,
            "form_data": self.form_data,
            "document_ids": self.document_ids,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "next_action": self.next_action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ApplicationTimeline(Base):
    __tablename__ = "application_timeline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=True)
    note = Column(Text, nullable=True)
    metadata_extra = Column(JSONB, default=dict, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "application_id": str(self.application_id),
            "event_type": self.event_type,
            "status": self.status,
            "note": self.note,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
