import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class AgentTaskStatus(str):
    CREATED = "created"
    PLANNING = "planning"
    WAITING_FOR_USER = "waiting_for_user"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTaskType(str):
    NEW_APPLICATION = "new_application"
    UPDATE_RECORD = "update_record"
    TRACK_APPLICATION = "track_application"
    RAISE_GRIEVANCE = "raise_grievance"
    CHECK_ELIGIBILITY = "check_eligibility"
    DISCOVER_SERVICE = "discover_service"
    OTHER = "other"


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_type = Column(String(50), default=AgentTaskType.OTHER, nullable=False, index=True)
    intent = Column(String(255), nullable=True)
    service_query = Column(String(500), nullable=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True, index=True)
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=True)
    status = Column(String(30), default=AgentTaskStatus.CREATED, nullable=False, index=True)
    current_state = Column(String(50), nullable=True)
    input_data = Column(JSONB, default=dict, nullable=False)
    output_data = Column(JSONB, default=dict, nullable=True)
    error_data = Column(JSONB, default=dict, nullable=True)
    recovery_attempts = Column(JSONB, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "task_type": self.task_type,
            "intent": self.intent,
            "service_query": self.service_query,
            "service_id": str(self.service_id) if self.service_id else None,
            "jurisdiction_id": str(self.jurisdiction_id) if self.jurisdiction_id else None,
            "application_id": str(self.application_id) if self.application_id else None,
            "status": self.status,
            "current_state": self.current_state,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_data": self.error_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
