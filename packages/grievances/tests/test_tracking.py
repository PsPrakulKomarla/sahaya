import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock
from packages.grievances.models import (
    Grievance,
    GrievanceStatus,
    GrievanceCategory,
    GrievanceTimelineEvent,
    utcnow,
)
from packages.grievances.tracking import GrievanceTrackingService
from packages.grievances.ports import GrievanceTrackingAdapter


class MockTrackingAdapter(GrievanceTrackingAdapter):
    def __init__(self, return_value: dict):
        self._return_value = return_value

    def track(self, reference_number: str) -> dict:
        return self._return_value


class MockSequenceTrackingAdapter(GrievanceTrackingAdapter):
    def __init__(self, status_sequence: list[str]):
        self._sequence = status_sequence
        self._index = 0

    def track(self, reference_number: str) -> dict:
        if self._index < len(self._sequence):
            status = self._sequence[self._index]
            self._index += 1
        else:
            status = self._sequence[-1]
        return {"source_status": status}


class TestGrievanceTrackingService:
    def _make_grievance(self, **kwargs):
        defaults = {
            "user_id": uuid4(),
            "service_id": "income_certificate",
            "subject": "Test",
            "description": "Test",
            "category": GrievanceCategory.APPLICATION_DELAY,
        }
        defaults.update(kwargs)
        return Grievance(**defaults)

    def test_track_without_adapter(self):
        service = GrievanceTrackingService()
        grievance = self._make_grievance()
        result = service.track(grievance)
        assert result.source_status == "unsubmitted"
        assert result.normalized_status == GrievanceStatus.DRAFT
        assert result.status_changed is False

    def test_track_without_reference(self):
        adapter = MockTrackingAdapter({"source_status": "processing"})
        service = GrievanceTrackingService(adapter)
        grievance = self._make_grievance()
        result = service.track(grievance)
        assert result.source_status == "unsubmitted"

    def test_track_status_change(self):
        adapter = MockTrackingAdapter({"source_status": "under examination"})
        service = GrievanceTrackingService(adapter)
        grievance = self._make_grievance(
            official_reference_number="REF123",
            status=GrievanceStatus.SUBMITTED,
        )
        result = service.track(grievance)
        assert result.source_status == "under examination"
        assert result.normalized_status == GrievanceStatus.PROCESSING
        assert result.status_changed is True
        assert grievance.status == GrievanceStatus.PROCESSING

    def test_track_no_status_change(self):
        adapter = MockTrackingAdapter({"source_status": "processing"})
        service = GrievanceTrackingService(adapter)
        grievance = self._make_grievance(
            official_reference_number="REF123",
            status=GrievanceStatus.PROCESSING,
        )
        result = service.track(grievance)
        assert result.status_changed is False
        assert grievance.status == GrievanceStatus.PROCESSING

    def test_track_resolved_sets_completed_at(self):
        adapter = MockTrackingAdapter({"source_status": "resolved"})
        service = GrievanceTrackingService(adapter)
        grievance = self._make_grievance(
            official_reference_number="REF123",
            status=GrievanceStatus.PROCESSING,
        )
        result = service.track(grievance)
        assert result.normalized_status == GrievanceStatus.RESOLVED
        assert grievance.completed_at is not None
        assert any(e.event == GrievanceTimelineEvent.STATUS_CHANGED for e in grievance.timeline)

    def test_label_method(self):
        assert GrievanceTrackingService.label(GrievanceStatus.RESOLVED) == "Resolved"
        assert GrievanceTrackingService.label(GrievanceStatus.PROCESSING) == "Processing"