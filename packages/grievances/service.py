"""Grievance Service — full lifecycle management."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from packages.grievances.models import (
    Grievance,
    GrievanceCategory,
    GrievanceDraft,
    GrievanceStatus,
    GrievanceFact,
    FactType,
    utcnow,
    can_transition,
)
from packages.grievances.categories import GrievanceCategoryRegistry, default_registry
from packages.grievances.composer import GrievanceComposer, make_fact
from packages.grievances.ports import (
    GrievanceRepositoryPort,
    ApprovalPort,
    ServiceAdapterPort,
    GrievanceTrackingAdapter,
)
from packages.grievances.tracking import GrievanceTrackingService
from packages.grievances.errors import (
    GrievanceNotFound,
    GrievanceNotOwned,
    InvalidStateTransition,
    ApprovalRequired,
    ApprovalInvalidated,
    CapabilityUnsupportedError,
    AmbiguousApplication,
    GrievanceSubmissionFailed,
)
from packages.services.base.models import ServiceCapability
from packages.services.registry.registry import ServiceRegistry


class GrievanceService:
    """Full lifecycle management for grievances."""

    def __init__(
        self,
        repository: GrievanceRepositoryPort,
        approval_port: ApprovalPort,
        service_registry: ServiceRegistry | None = None,
        category_registry: GrievanceCategoryRegistry | None = None,
        tracking_service: GrievanceTrackingService | None = None,
        composer: GrievanceComposer | None = None,
    ) -> None:
        self._repo = repository
        self._approval = approval_port
        self._registry = service_registry or ServiceRegistry()
        self._categories = category_registry or default_registry
        self._tracking = tracking_service or GrievanceTrackingService()
        self._composer = composer or GrievanceComposer()

    def _transition(self, grievance: Grievance, target: GrievanceStatus) -> None:
        if not can_transition(grievance.status, target):
            raise InvalidStateTransition(grievance.status.value, target.value)
        grievance.status = target
        grievance.updated_at = utcnow()

    async def create_draft(
        self,
        user_id: UUID,
        service_id: str,
        user_issue: str,
        language: str = "en",
        application_id: UUID | None = None,
        jurisdiction: str | None = None,
    ) -> Grievance:
        """Create a new grievance draft from user's issue description."""
        adapter = self._registry.get_service(service_id)
        if not adapter:
            raise ValueError(f"Service '{service_id}' not found")

        caps = adapter.get_capabilities()
        if ServiceCapability.RAISE_GRIEVANCE not in caps:
            raise CapabilityUnsupportedError("RAISE_GRIEVANCE", service_id)

        category = self._categories.detect(user_issue, language)
        category_def = self._categories.get(category)

        meta = adapter.metadata()
        service_name = getattr(meta, "display_name", service_id)

        draft = self._composer.compose(
            user_issue=user_issue,
            application_reference=None,
            service=service_name,
            jurisdiction=jurisdiction,
            category_label=category_def.label if category_def else category.value,
            language=language,
        )

        grievance = Grievance(
            user_id=user_id,
            application_id=application_id,
            service_id=service_id,
            jurisdiction=jurisdiction,
            subject=draft.subject,
            description=draft.description,
            category=category,
            facts=draft.facts,
            attachments=draft.attachments,
        )
        grievance.append_event(GrievanceTimelineEvent.CREATED, note="Grievance draft created")
        self._transition(grievance, GrievanceStatus.DRAFT)

        return await self._repo.save(grievance)

    async def link_application(
        self,
        grievance_id: UUID,
        user_id: UUID,
        application_id: UUID,
    ) -> Grievance:
        """Link a grievance to a specific application."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)

        grievance.application_id = application_id
        grievance.updated_at = utcnow()
        grievance.append_event(
            GrievanceTimelineEvent.DRAFT_UPDATED, note=f"Linked to application {application_id}"
        )
        return await self._repo.save(grievance)

    async def update_draft(
        self,
        grievance_id: UUID,
        user_id: UUID,
        *,
        subject: str | None = None,
        description: str | None = None,
        category: GrievanceCategory | None = None,
        jurisdiction: str | None = None,
        facts: list[GrievanceFact] | None = None,
        attachments: list[str] | None = None,
    ) -> Grievance:
        """Update a grievance draft (only in DRAFT or PREPARING state)."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)

        if grievance.status not in (GrievanceStatus.DRAFT, GrievanceStatus.PREPARING):
            raise InvalidStateTransition(
                grievance.status.value, "DRAFT/PREPARING (update)"
            )

        if subject is not None:
            grievance.subject = subject
        if description is not None:
            grievance.description = description
        if category is not None:
            grievance.category = category
        if jurisdiction is not None:
            grievance.jurisdiction = jurisdiction
        if facts is not None:
            grievance.facts = facts
        if attachments is not None:
            grievance.attachments = attachments

        grievance.updated_at = utcnow()
        grievance.append_event(GrievanceTimelineEvent.DRAFT_UPDATED, note="Draft updated")
        self._transition(grievance, GrievanceStatus.PREPARING)

        return await self._repo.save(grievance)

    async def prepare_for_review(
        self,
        grievance_id: UUID,
        user_id: UUID,
    ) -> Grievance:
        """Mark draft as ready for human review."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)

        if grievance.status not in (GrievanceStatus.DRAFT, GrievanceStatus.PREPARING):
            raise InvalidStateTransition(
                grievance.status.value, GrievanceStatus.READY_FOR_REVIEW.value
            )

        self._transition(grievance, GrievanceStatus.READY_FOR_REVIEW)
        grievance.append_event(
            GrievanceTimelineEvent.REVIEW_REQUESTED, note="Ready for human review"
        )
        return await self._repo.save(grievance)

    async def request_approval(
        self,
        grievance_id: UUID,
        user_id: UUID,
    ) -> tuple[Grievance, str]:
        """Request human approval for grievance submission."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)

        if grievance.status != GrievanceStatus.READY_FOR_REVIEW:
            raise InvalidStateTransition(
                grievance.status.value, GrievanceStatus.AWAITING_APPROVAL.value
            )

        grievance.approval_fingerprint = grievance.to_draft().fingerprint()

        approval_id = await self._approval.request_approval(
            user_id=user_id,
            action_type="SUBMIT_GRIEVANCE",
            summary=f"Submit grievance: {grievance.subject}",
            metadata={
                "grievance_id": str(grievance_id),
                "service_id": grievance.service_id,
                "category": grievance.category.value,
                "fingerprint": grievance.approval_fingerprint,
            },
        )
        grievance.approval_id = approval_id
        self._transition(grievance, GrievanceStatus.AWAITING_APPROVAL)
        grievance.append_event(
            GrievanceTimelineEvent.APPROVAL_REQUESTED,
            note=f"Approval requested (id: {approval_id})",
        )
        return await self._repo.save(grievance), approval_id

    async def grant_approval(
        self,
        grievance_id: UUID,
        approval_id: str,
    ) -> Grievance:
        """Record human approval (validates fingerprint)."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)

        if grievance.status != GrievanceStatus.AWAITING_APPROVAL:
            raise InvalidStateTransition(
                grievance.status.value, "APPROVED"
            )

        if grievance.approval_id != approval_id:
            raise ApprovalInvalidated()

        current_fingerprint = grievance.to_draft().fingerprint()
        if grievance.approval_fingerprint != current_fingerprint:
            grievance.append_event(
                GrievanceTimelineEvent.APPROVAL_INVALIDATED,
                note="Grievance changed after approval; approval invalidated",
            )
            grievance.approval_id = None
            grievance.approval_fingerprint = None
            self._transition(grievance, GrievanceStatus.READY_FOR_REVIEW)
            raise ApprovalInvalidated()

        if not await self._approval.is_approved(approval_id):
            raise ApprovalInvalidated()

        grievance.append_event(
            GrievanceTimelineEvent.APPROVAL_GRANTED, note="Approval granted by user"
        )
        self._transition(grievance, GrievanceStatus.SUBMITTED)
        return await self._repo.save(grievance)

    async def reject_approval(
        self,
        grievance_id: UUID,
        approval_id: str,
    ) -> Grievance:
        """Record human rejection of approval."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)

        if grievance.status != GrievanceStatus.AWAITING_APPROVAL:
            raise InvalidStateTransition(
                grievance.status.value, "REJECTED"
            )

        if grievance.approval_id != approval_id:
            raise GrievanceError("Approval ID mismatch")

        grievance.approval_id = None
        grievance.approval_fingerprint = None
        self._transition(grievance, GrievanceStatus.READY_FOR_REVIEW)
        grievance.append_event(
            GrievanceTimelineEvent.APPROVAL_REJECTED, note="Approval rejected by user"
        )
        return await self._repo.save(grievance)

    async def submit(
        self,
        grievance_id: UUID,
        browser_agent: Any,
        safety_policy: Any,
    ) -> Grievance:
        """Submit the approved grievance to the government portal."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)

        if grievance.status != GrievanceStatus.SUBMITTED:
            raise InvalidStateTransition(grievance.status.value, "SUBMITTED (execute)")

        if grievance.approval_id is None:
            raise ApprovalRequired()

        if not await self._approval.validate_approval(grievance.approval_id):
            raise ApprovalInvalidated()

        adapter = self._registry.get_service(grievance.service_id)
        if not adapter:
            raise GrievanceSubmissionFailed(f"Service '{grievance.service_id}' not found")

        caps = adapter.get_capabilities()
        if ServiceCapability.RAISE_GRIEVANCE not in caps:
            raise CapabilityUnsupportedError("RAISE_GRIEVANCE", grievance.service_id)

        try:
            result = await adapter.raise_grievance(
                grievance=grievance.to_draft(),
                browser_agent=browser_agent,
                safety_policy=safety_policy,
            )
        except Exception as e:
            grievance.status = GrievanceStatus.FAILED
            grievance.append_event(
                GrievanceTimelineEvent.FAILED, note=f"Submission failed: {e}"
            )
            await self._repo.save(grievance)
            raise GrievanceSubmissionFailed(str(e))

        grievance.official_reference_number = result.official_reference_number
        grievance.source_status = result.source_status
        grievance.submitted_at = result.submitted_at
        grievance.status = GrievanceStatus.PROCESSING
        grievance.append_event(
            GrievanceTimelineEvent.SUBMITTED,
            note=f"Submitted with reference {result.official_reference_number}",
        )
        return await self._repo.save(grievance)

    async def track(
        self,
        grievance_id: UUID,
        user_id: UUID,
    ) -> tuple[Grievance, Any]:
        """Check grievance status against the portal."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)

        result = self._tracking.track(grievance)
        await self._repo.save(grievance)
        return grievance, result

    async def get_grievance(self, grievance_id: UUID, user_id: UUID) -> Grievance:
        """Get a grievance by ID, enforcing ownership."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)
        return grievance

    async def list_grievances(self, user_id: UUID) -> list[Grievance]:
        """List all grievances for a user."""
        return await self._repo.find_by_user(user_id)

    async def cancel_grievance(self, grievance_id: UUID, user_id: UUID) -> Grievance:
        """Cancel a grievance (only in certain states)."""
        grievance = await self._repo.get(grievance_id)
        if not grievance:
            raise GrievanceNotFound(grievance_id)
        if grievance.user_id != user_id:
            raise GrievanceNotOwned(user_id)

        if not can_transition(grievance.status, GrievanceStatus.CANCELLED):
            raise InvalidStateTransition(grievance.status.value, GrievanceStatus.CANCELLED.value)

        grievance.status = GrievanceStatus.CANCELLED
        grievance.updated_at = utcnow()
        grievance.append_event(
            GrievanceTimelineEvent.CANCELLED, note="Cancelled by user"
        )
        return await self._repo.save(grievance)

    async def detect_category(
        self,
        text: str,
        language: str = "en",
    ) -> GrievanceCategory:
        """Detect grievance category from free text."""
        return self._categories.detect(text, language)