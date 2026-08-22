"""Grievance Engine — domain models.

Transport- and storage-agnostic. Internal representations stay
language-independent; localized strings are produced only at the presentation
boundary.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _StrEnum(str, Enum):
    """Backport of StrEnum for Python < 3.11."""
    def __str__(self) -> str:
        return self.value


class GrievanceCategory(_StrEnum):
    APPLICATION_DELAY = "application_delay"
    APPLICATION_REJECTION = "application_rejection"
    DOCUMENT_ISSUE = "document_issue"
    INCORRECT_INFORMATION = "incorrect_information"
    PAYMENT_ISSUE = "payment_issue"
    PORTAL_PROBLEM = "portal_problem"
    SERVICE_UNAVAILABLE = "service_unavailable"
    OTHER = "other"


class GrievanceStatus(_StrEnum):
    DRAFT = "draft"
    PREPARING = "preparing"
    READY_FOR_REVIEW = "ready_for_review"
    AWAITING_APPROVAL = "awaiting_approval"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    ACTION_REQUIRED = "action_required"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FactType(_StrEnum):
    VERIFIED_FACT = "verified_fact"
    USER_CLAIM = "user_claim"
    INFERENCE = "inference"


class GrievanceTimelineEvent(_StrEnum):
    CREATED = "grievance_created"
    DRAFT_UPDATED = "draft_updated"
    REVIEW_REQUESTED = "review_requested"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    APPROVAL_INVALIDATED = "approval_invalidated"
    SUBMITTED = "submitted"
    STATUS_CHANGED = "status_changed"
    ACTION_REQUIRED = "action_required"
    RESOLVED = "resolved"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GrievanceFact(BaseModel):
    """A single assertion in a grievance draft.

    ``fact_type`` distinguishes verified facts, user claims, and inferences so
    the system never presents an inference as an established fact.
    """

    type: FactType
    statement: str
    source: str | None = None

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        dump = super().model_dump(**kwargs)
        if isinstance(dump.get("type"), FactType):
            dump["type"] = dump["type"].value
        return dump


class GrievanceDraft(BaseModel):
    """An editable pre-submission grievance."""

    subject: str
    description: str
    category: GrievanceCategory
    service: str
    jurisdiction: str | None = None
    application_reference: str | None = None
    facts: list[GrievanceFact] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)

    def fingerprint(self) -> str:
        """Stable fingerprint used to invalidate stale approvals."""
        import hashlib

        canonical = {
            "subject": self.subject.strip().lower(),
            "description": self.description.strip().lower(),
            "category": self.category.value,
            "application_reference": self.application_reference,
            "facts": [f.statement.strip().lower() for f in self.facts],
            "attachments": sorted(self.attachments),
        }
        raw = repr(sorted(canonical.items())).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


class GrievanceTimelineEntry(BaseModel):
    event: GrievanceTimelineEvent
    note: str = ""
    occurred_at: datetime = Field(default_factory=utcnow)


class SubmissionResult(BaseModel):
    official_reference_number: str
    source_status: str
    submitted_at: datetime = Field(default_factory=utcnow)


class TrackResult(BaseModel):
    official_reference_number: str
    source_status: str
    normalized_status: GrievanceStatus
    status_changed: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class Grievance(BaseModel):
    """Domain aggregate for a grievance owned by a user."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    application_id: UUID | None = None
    service_id: str | None = None
    jurisdiction: str | None = None
    subject: str
    description: str
    category: GrievanceCategory
    status: GrievanceStatus = GrievanceStatus.DRAFT
    official_reference_number: str | None = None
    source_status: str | None = None
    facts: list[GrievanceFact] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)
    approval_fingerprint: str | None = None
    approval_id: str | None = None
    timeline: list[GrievanceTimelineEntry] = Field(default_factory=list)
    metadata_extra: dict[str, Any] = Field(default_factory=dict)
    submitted_at: datetime | None = None
    last_checked_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def to_draft(self) -> GrievanceDraft:
        return GrievanceDraft(
            subject=self.subject,
            description=self.description,
            category=self.category,
            service=self.service_id or "",
            jurisdiction=self.jurisdiction,
            application_reference=self.official_reference_number,
            facts=self.facts,
            attachments=self.attachments,
        )

    def append_event(self, event: GrievanceTimelineEvent, note: str = "") -> None:
        self.timeline.append(GrievanceTimelineEntry(event=event, note=note))
        self.updated_at = utcnow()


VALID_TRANSITIONS: dict[GrievanceStatus, set[GrievanceStatus]] = {
    GrievanceStatus.DRAFT: {
        GrievanceStatus.PREPARING,
        GrievanceStatus.READY_FOR_REVIEW,
        GrievanceStatus.CANCELLED,
    },
    GrievanceStatus.PREPARING: {
        GrievanceStatus.READY_FOR_REVIEW,
        GrievanceStatus.DRAFT,
        GrievanceStatus.CANCELLED,
    },
    GrievanceStatus.READY_FOR_REVIEW: {
        GrievanceStatus.AWAITING_APPROVAL,
        GrievanceStatus.DRAFT,
        GrievanceStatus.CANCELLED,
    },
    GrievanceStatus.AWAITING_APPROVAL: {
        GrievanceStatus.SUBMITTED,
        GrievanceStatus.READY_FOR_REVIEW,
        GrievanceStatus.CANCELLED,
    },
    GrievanceStatus.SUBMITTED: {
        GrievanceStatus.PROCESSING,
        GrievanceStatus.ACTION_REQUIRED,
        GrievanceStatus.RESOLVED,
        GrievanceStatus.REJECTED,
        GrievanceStatus.FAILED,
    },
    GrievanceStatus.PROCESSING: {
        GrievanceStatus.ACTION_REQUIRED,
        GrievanceStatus.RESOLVED,
        GrievanceStatus.REJECTED,
        GrievanceStatus.FAILED,
    },
    GrievanceStatus.ACTION_REQUIRED: {
        GrievanceStatus.PROCESSING,
        GrievanceStatus.SUBMITTED,
        GrievanceStatus.CANCELLED,
    },
    GrievanceStatus.RESOLVED: set(),
    GrievanceStatus.REJECTED: set(),
    GrievanceStatus.FAILED: {GrievanceStatus.SUBMITTED},
    GrievanceStatus.CANCELLED: set(),
}


def can_transition(current: GrievanceStatus, target: GrievanceStatus) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())