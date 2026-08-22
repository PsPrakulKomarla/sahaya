"""AuditEventService records audit events for the agent system.

Sensitive information is redacted from audit events.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    """Types of audit events."""
    TASK_CREATED = "TASK_CREATED"
    TASK_STARTED = "TASK_STARTED"
    STATE_CHANGED = "STATE_CHANGED"
    SERVICE_RESOLVED = "SERVICE_RESOLVED"
    PLAN_CREATED = "PLAN_CREATED"
    STEP_STARTED = "STEP_STARTED"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    BROWSER_ACTION = "BROWSER_ACTION"
    TASK_CANCELLED = "TASK_CANCELLED"
    SAFETY_EVALUATION = "SAFETY_EVALUATION"


class AuditEvent(BaseModel):
    """An immutable audit event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    user_id: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata_redacted: Dict[str, Any] = Field(default_factory=dict)


class AuditEventService:
    """Records audit events.

    Events are immutable — once created, they cannot be modified.
    Sensitive data is redacted before storage.
    """

    SENSITIVE_KEYS = {
        "password", "password_hash", "secret", "token",
        "aadhaar", "ssn", "credit_card", "bank_account",
        "otp", "pin",
    }

    def __init__(self) -> None:
        self._events: List[AuditEvent] = []

    def record(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Record an audit event."""
        redacted = self._redact(metadata or {})

        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            task_id=task_id,
            metadata_redacted=redacted,
        )
        self._events.append(event)
        return event

    def get_events(
        self,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> List[AuditEvent]:
        """Query audit events."""
        results = self._events
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if task_id:
            results = [e for e in results if e.task_id == task_id]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        return results

    def _redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields from metadata."""
        redacted = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact(value)
            else:
                redacted[key] = value
        return redacted
