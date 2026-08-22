import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class AuditEventType(str):
    AGENT_STARTED = "agent_started"
    SERVICE_RESOLVED = "service_resolved"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_VERIFIED = "document_verified"
    WORKFLOW_STARTED = "workflow_started"
    BROWSER_ACTION = "browser_action"
    RECOVERY_TRIGGERED = "recovery_triggered"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    APPLICATION_SUBMITTED = "application_submitted"
    STATUS_UPDATED = "status_updated"
    GRIEVANCE_SUBMITTED = "grievance_submitted"
    USER_LOGIN = "user_login"
    ERROR_OCCURRED = "error_occurred"


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    metadata_redacted = Column(JSONB, default=dict, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "task_id": str(self.task_id) if self.task_id else None,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata_redacted": self.metadata_redacted,
        }
