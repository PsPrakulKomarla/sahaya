import pytest
from uuid import uuid4
import time
from packages.grievances.models import (
    GrievanceCategory,
    GrievanceStatus,
    FactType,
    GrievanceTimelineEvent,
    GrievanceFact,
    GrievanceDraft,
    GrievanceTimelineEntry,
    Grievance,
    SubmissionResult,
    TrackResult,
    utcnow,
    can_transition,
    VALID_TRANSITIONS,
)


class TestGrievanceModels:
    def test_grievance_category_enum(self):
        assert GrievanceCategory.APPLICATION_DELAY == "application_delay"
        assert GrievanceCategory.OTHER == "other"

    def test_grievance_status_enum(self):
        assert GrievanceStatus.DRAFT == "draft"
        assert GrievanceStatus.AWAITING_APPROVAL == "awaiting_approval"
        assert GrievanceStatus.RESOLVED == "resolved"

    def test_fact_type_enum(self):
        assert FactType.VERIFIED_FACT == "verified_fact"
        assert FactType.USER_CLAIM == "user_claim"
        assert FactType.INFERENCE == "inference"

    def test_grievance_fact(self):
        fact = GrievanceFact(type=FactType.VERIFIED_FACT, statement="Test fact", source="user")
        assert fact.type == FactType.VERIFIED_FACT
        assert fact.statement == "Test fact"
        assert fact.source == "user"

    def test_grievance_fact_dump(self):
        fact = GrievanceFact(type=FactType.VERIFIED_FACT, statement="Test fact")
        dump = fact.model_dump()
        assert dump["type"] == "verified_fact"

    def test_grievance_draft(self):
        draft = GrievanceDraft(
            subject="Test Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
            service="Income Certificate",
        )
        assert draft.subject == "Test Subject"
        assert draft.category == GrievanceCategory.APPLICATION_DELAY

    def test_grievance_draft_fingerprint(self):
        draft1 = GrievanceDraft(
            subject="Test Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
            service="Income Certificate",
        )
        draft2 = GrievanceDraft(
            subject="Test Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
            service="Income Certificate",
        )
        assert draft1.fingerprint() == draft2.fingerprint()

        draft3 = GrievanceDraft(
            subject="Different Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
            service="Income Certificate",
        )
        assert draft1.fingerprint() != draft3.fingerprint()

    def test_grievance_timeline_entry(self):
        entry = GrievanceTimelineEntry(
            event=GrievanceTimelineEvent.CREATED,
            note="Created",
        )
        assert entry.event == GrievanceTimelineEvent.CREATED
        assert entry.note == "Created"
        assert entry.occurred_at is not None

    def test_grievance_creation(self):
        grievance = Grievance(
            user_id=uuid4(),
            service_id="income_certificate",
            subject="Test Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
        )
        assert grievance.id is not None
        assert grievance.status == GrievanceStatus.DRAFT
        assert grievance.created_at is not None

    def test_grievance_to_draft(self):
        grievance = Grievance(
            user_id=uuid4(),
            service_id="income_certificate",
            subject="Test Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
            jurisdiction="Karnataka",
        )
        draft = grievance.to_draft()
        assert draft.subject == grievance.subject
        assert draft.category == grievance.category
        assert draft.jurisdiction == "Karnataka"

    def test_grievance_append_event(self):
        grievance = Grievance(
            user_id=uuid4(),
            service_id="income_certificate",
            subject="Test Subject",
            description="Test Description",
            category=GrievanceCategory.APPLICATION_DELAY,
        )
        initial_time = grievance.updated_at
        time.sleep(0.01)  # Ensure timestamp difference
        grievance.append_event(GrievanceTimelineEvent.CREATED, "Test note")
        assert len(grievance.timeline) == 1
        assert grievance.timeline[0].event == GrievanceTimelineEvent.CREATED
        assert grievance.updated_at >= initial_time

    def test_submission_result(self):
        result = SubmissionResult(
            official_reference_number="REF123",
            source_status="submitted",
        )
        assert result.official_reference_number == "REF123"

    def test_track_result(self):
        result = TrackResult(
            official_reference_number="REF123",
            source_status="processing",
            normalized_status=GrievanceStatus.PROCESSING,
            status_changed=True,
        )
        assert result.status_changed is True


class TestStateTransitions:
    def test_valid_transitions(self):
        assert can_transition(GrievanceStatus.DRAFT, GrievanceStatus.PREPARING)
        assert can_transition(GrievanceStatus.DRAFT, GrievanceStatus.CANCELLED)
        assert can_transition(GrievanceStatus.PREPARING, GrievanceStatus.READY_FOR_REVIEW)
        assert can_transition(GrievanceStatus.READY_FOR_REVIEW, GrievanceStatus.AWAITING_APPROVAL)
        assert can_transition(GrievanceStatus.AWAITING_APPROVAL, GrievanceStatus.SUBMITTED)
        assert can_transition(GrievanceStatus.SUBMITTED, GrievanceStatus.PROCESSING)
        assert can_transition(GrievanceStatus.PROCESSING, GrievanceStatus.RESOLVED)
        assert can_transition(GrievanceStatus.FAILED, GrievanceStatus.SUBMITTED)

    def test_invalid_transitions(self):
        assert not can_transition(GrievanceStatus.DRAFT, GrievanceStatus.SUBMITTED)
        assert not can_transition(GrievanceStatus.RESOLVED, GrievanceStatus.PROCESSING)
        assert not can_transition(GrievanceStatus.CANCELLED, GrievanceStatus.DRAFT)

    def test_transition_map_completeness(self):
        for status in GrievanceStatus:
            assert status in VALID_TRANSITIONS