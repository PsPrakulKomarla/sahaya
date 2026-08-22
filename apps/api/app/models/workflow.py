import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class WorkflowStatus(str):
    DRAFT = "draft"
    LEARNING = "learning"
    ACTIVE = "active"
    OUTDATED = "outdated"
    DISABLED = "disabled"


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
    workflow_definition = Column(JSONB, nullable=False, default=dict)
    confidence = Column(Float, nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
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
            "workflow_definition": self.workflow_definition,
            "confidence": self.confidence,
            "last_verified_at": self.last_verified_at.isoformat()
            if self.last_verified_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
