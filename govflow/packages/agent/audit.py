"""Audit logging service.

Provides structured audit logging with PII redaction.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.audit_event import AuditEvent

logger = get_logger(__name__)


class AuditEventType(str, Enum):
    """Standard audit event types."""

    # Authentication
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGED = "password_changed"

    # Authorization
    PERMISSION_DENIED = "permission_denied"
    ROLE_CHANGED = "role_changed"

    # Task lifecycle
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"

    # Service resolution
    SERVICE_RESOLVED = "service_resolved"
    SERVICE_RESOLUTION_FAILED = "service_resolution_failed"

    # Planning
    PLAN_CREATED = "plan_created"
    PLAN_VALIDATED = "plan_validated"

    # Execution
    STEP_EXECUTED = "step_executed"
    STEP_FAILED = "step_failed"
    STEP_RECOVERED = "step_recovered"

    # Safety & Approval
    SAFETY_EVALUATION = "safety_evaluation"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    APPROVAL_EXPIRED = "approval_expired"

    # Browser
    BROWSER_NAVIGATED = "browser_navigated"
    BROWSER_ACTION = "browser_action"
    BROWSER_RECOVERY = "browser_recovery"

    # Workflow memory
    WORKFLOW_LEARNED = "workflow_learned"
    WORKFLOW_REUSED = "workflow_reused"
    WORKFLOW_PROMOTED = "workflow_promoted"
    WORKFLOW_INVALIDATED = "workflow_invalidated"

    # Documents
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_PROCESSED = "document_processed"
    DOCUMENT_VERIFIED = "document_verified"
    DOCUMENT_REJECTED = "document_rejected"

    # Applications
    APPLICATION_CREATED = "application_created"
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_UPDATED = "application_updated"
    APPLICATION_TRACKED = "application_tracked"

    # Grievances
    GRIEVANCE_CREATED = "grievance_created"
    GRIEVANCE_SUBMITTED = "grievance_submitted"

    # Security
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    URL_BLOCKED = "url_blocked"
    SSRF_ATTEMPT = "ssrf_attempt"
    SUSPICIOUS_REDIRECT = "suspicious_redirect"


class AuditMetadata(BaseModel):
    """Structured audit metadata with automatic PII redaction."""

    # Request context
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Resource identifiers (not PII)
    service_id: Optional[str] = None
    workflow_id: Optional[str] = None
    document_id: Optional[str] = None
    application_id: Optional[str] = None
    task_id: Optional[str] = None
    approval_id: Optional[str] = None

    # Action details
    action_type: Optional[str] = None
    action_description: Optional[str] = None
    status: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # Counts/metrics
    duration_ms: Optional[int] = None
    retry_count: Optional[int] = None
    redirect_count: Optional[int] = None

    # Security flags
    security_violation: bool = False
    blocked: bool = False
    reason: Optional[str] = None

    model_config = {"extra": "allow"}

    def redacted(self) -> dict[str, Any]:
        """Return metadata with PII redacted."""
        data = self.model_dump(exclude_none=True)
        # Additional PII fields that might slip through
        pii_fields = {
            "email", "phone", "ssn", "aadhaar", "pan", "passport",
            "credit_card", "bank_account", "password", "token",
            "secret", "key", "authorization", "cookie", "session"
        }
        for key in list(data.keys()):
            if any(pii in key.lower() for pii in pii_fields):
                data[key] = "[REDACTED]"
        return data


class AuditEventService:
    """Central audit event service.

    Provides structured audit logging with:
    - PII redaction
    - Database persistence
    - Structured metadata
    """

    def __init__(self):
        self._enabled = True

    def record(
        self,
        event_type: str,
        user_id: Optional[UUID] = None,
        task_id: Optional[str] = None,
        metadata: Optional[AuditMetadata] = None,
    ) -> None:
        """Record an audit event.

        Args:
            event_type: Type of event (use AuditEventType enum)
            user_id: Associated user ID
            task_id: Associated task ID
            metadata: Structured metadata
        """
        if not self._enabled:
            return

        meta = metadata or AuditMetadata()
        meta.task_id = meta.task_id or task_id

        # Log to structured logger
        log_data = {
            "event_type": event_type,
            "user_id": str(user_id) if user_id else None,
            "task_id": task_id,
            **meta.redacted(),
        }
        logger.info("audit_event", **log_data)

        # TODO: Persist to database (requires async context)
        # This will be handled by the async version

    async def record_async(
        self,
        event_type: str,
        user_id: Optional[UUID] = None,
        task_id: Optional[str] = None,
        metadata: Optional[AuditMetadata] = None,
    ) -> AuditEvent:
        """Record an audit event asynchronously with database persistence.

        Args:
            event_type: Type of event
            user_id: Associated user ID
            task_id: Associated task ID
            metadata: Structured metadata

        Returns:
            The created AuditEvent record
        """
        if not self._enabled:
            return None

        meta = metadata or AuditMetadata()
        meta.task_id = meta.task_id or task_id

        # Log to structured logger
        log_data = {
            "event_type": event_type,
            "user_id": str(user_id) if user_id else None,
            "task_id": task_id,
            **meta.redacted(),
        }
        logger.info("audit_event", **log_data)

        # Persist to database
        async for db in get_db():
            audit_event = AuditEvent(
                event_type=event_type,
                user_id=user_id,
                task_id=task_id,
                metadata=meta.redacted(),
            )
            db.add(audit_event)
            await db.commit()
            await db.refresh(audit_event)
            return audit_event

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False


# Global instance
audit_service = AuditEventService()