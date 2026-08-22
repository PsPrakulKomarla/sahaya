import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class WorkflowStatus(str):
    DRAFT = "draft"
    LEARNING = "learning"
    VALIDATED = "validated"
    ACTIVE = "active"
    OUTDATED = "outdated"
    DISABLED = "disabled"
    FAILED = "failed"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jurisdiction_id = Column(
        UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True, index=True
    )
    workflow_version = Column(String(50), nullable=False)
    status = Column(String(20), default=WorkflowStatus.DRAFT, nullable=False, index=True)
    source = Column(String(30), default="exploration", nullable=False)
    workflow_definition = Column(JSONB, nullable=False, default=dict)
    confidence = Column(Float, nullable=True, default=0.0)
    execution_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    recovery_count = Column(Integer, nullable=False, default=0)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "service_id": str(self.service_id),
            "jurisdiction_id": str(self.jurisdiction_id) if self.jurisdiction_id else None,
            "workflow_version": self.workflow_version,
            "status": self.status,
            "source": self.source,
            "workflow_definition": self.workflow_definition,
            "confidence": self.confidence,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "recovery_count": self.recovery_count,
            "last_verified_at": self.last_verified_at.isoformat()
            if self.last_verified_at
            else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
