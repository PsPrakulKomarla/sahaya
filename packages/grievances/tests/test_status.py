import pytest
from packages.grievances.status import normalize_status, STATUS_LABELS
from packages.grievances.models import GrievanceStatus


class TestStatusNormalization:
    def test_resolved_variations(self):
        assert normalize_status("resolved") == GrievanceStatus.RESOLVED
        assert normalize_status("closed") == GrievanceStatus.RESOLVED
        assert normalize_status("disposed") == GrievanceStatus.RESOLVED
        assert normalize_status("Case RESOLVED by officer") == GrievanceStatus.RESOLVED

    def test_rejected_variations(self):
        assert normalize_status("rejected") == GrievanceStatus.REJECTED
        assert normalize_status("dismissed") == GrievanceStatus.REJECTED
        assert normalize_status("rejected by department") == GrievanceStatus.REJECTED

    def test_processing_variations(self):
        assert normalize_status("processing") == GrievanceStatus.PROCESSING
        assert normalize_status("under examination") == GrievanceStatus.PROCESSING
        assert normalize_status("under review") == GrievanceStatus.PROCESSING
        assert normalize_status("with the department") == GrievanceStatus.PROCESSING
        assert normalize_status("forwarded") == GrievanceStatus.PROCESSING
        assert normalize_status("pending") == GrievanceStatus.PROCESSING
        assert normalize_status("in progress") == GrievanceStatus.PROCESSING

    def test_action_required_variations(self):
        assert normalize_status("action required") == GrievanceStatus.ACTION_REQUIRED
        assert normalize_status("awaiting response") == GrievanceStatus.ACTION_REQUIRED
        assert normalize_status("awaiting documents") == GrievanceStatus.ACTION_REQUIRED
        assert normalize_status("additional information required") == GrievanceStatus.ACTION_REQUIRED
        assert normalize_status("more information required") == GrievanceStatus.ACTION_REQUIRED

    def test_submitted_variations(self):
        assert normalize_status("registered") == GrievanceStatus.SUBMITTED
        assert normalize_status("complaint registered") == GrievanceStatus.SUBMITTED
        assert normalize_status("submitted") == GrievanceStatus.SUBMITTED

    def test_failed_variations(self):
        assert normalize_status("failed") == GrievanceStatus.FAILED
        assert normalize_status("error") == GrievanceStatus.FAILED

    def test_none_returns_draft(self):
        assert normalize_status(None) == GrievanceStatus.DRAFT
        assert normalize_status("") == GrievanceStatus.DRAFT

    def test_unknown_returns_processing(self):
        assert normalize_status("unknown status xyz") == GrievanceStatus.PROCESSING

    def test_status_labels(self):
        assert STATUS_LABELS[GrievanceStatus.DRAFT] == "Draft"
        assert STATUS_LABELS[GrievanceStatus.RESOLVED] == "Resolved"
        assert STATUS_LABELS[GrievanceStatus.REJECTED] == "Rejected"