import os
import sys
import pytest
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.applications.application_service import ApplicationService
from packages.applications.tracking_service import ApplicationTrackingService


class TestApplicationService:
    def setup_method(self):
        self.service = ApplicationService()

    def test_create_draft(self):
        user_id = str(uuid.uuid4())
        result = self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi Kumar"},
            document_ids=["doc1", "doc2"],
        )
        assert result["id"]
        assert result["user_id"] == user_id
        assert result["service_id"] == "income_certificate"
        assert result["status"] == "draft"
        assert result["form_data"]["applicant_name"] == "Ravi Kumar"

    def test_update_draft(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
        )
        updated = self.service.update_draft(app, form_data={"applicant_name": "Ravi"})
        assert updated["form_data"]["applicant_name"] == "Ravi"

    def test_update_draft_invalidates_approval(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi"},
        )
        updated = self.service.update_draft(
            app, form_data={"applicant_name": "New Name"}, approval_id="approval-1"
        )
        assert updated.get("approval_invalidated") is True

    def test_validate_draft_valid(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi Kumar", "address": "Bengaluru"},
            document_ids=["doc1"],
        )
        result = self.service.validate_draft(app)
        assert result["valid"] is True

    def test_validate_draft_empty(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
        )
        result = self.service.validate_draft(app)
        assert result["valid"] is False
        assert "Form data is empty" in result["errors"]

    def test_validate_draft_missing_fields(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi"},
        )
        result = self.service.validate_draft(app)
        assert result["valid"] is False
        assert "address" in result["missing_fields"]

    def test_mark_ready_for_review_success(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi Kumar", "address": "Bengaluru"},
            document_ids=["doc1"],
        )
        result = self.service.mark_ready_for_review(app)
        assert result["success"] is True
        assert result["application"]["status"] == "ready_for_review"

    def test_mark_ready_for_review_failure(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
        )
        result = self.service.mark_ready_for_review(app)
        assert result["success"] is False

    def test_mark_awaiting_approval(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
        )
        result = self.service.mark_awaiting_approval(app)
        assert result["status"] == "awaiting_approval"

    def test_create_timeline_event(self):
        event = self.service.create_timeline_event(
            application_id=str(uuid.uuid4()),
            event_type="APPLICATION_CREATED",
            status="draft",
            note="Test event",
        )
        assert event["id"]
        assert event["event_type"] == "APPLICATION_CREATED"
        assert event["timestamp"]

    def test_get_timeline_sorted(self):
        events = [
            {"timestamp": "2026-08-02T00:00:00", "event_type": "EVENT_B"},
            {"timestamp": "2026-08-01T00:00:00", "event_type": "EVENT_A"},
        ]
        sorted_events = self.service.get_timeline(events)
        assert sorted_events[0]["event_type"] == "EVENT_A"
        assert sorted_events[1]["event_type"] == "EVENT_B"


class TestApplicationSubmit:
    def setup_method(self):
        from packages.services.registry.registry import ServiceRegistry
        from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter

        self.registry = ServiceRegistry()
        self.registry.register_service(MockIncomeCertificateAdapter())
        self.service = ApplicationService(registry=self.registry)

    @pytest.mark.asyncio
    async def test_submit_success(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi Kumar", "address": "Bengaluru", "annual_income": 500000},
            document_ids=["doc1"],
        )
        self.service.mark_ready_for_review(app)
        self.service.mark_awaiting_approval(app)

        result = await self.service.submit(app)
        assert result["success"] is True
        assert result["application"]["status"] == "submitted"
        assert result["application"]["reference_number"]

    @pytest.mark.asyncio
    async def test_submit_wrong_status(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
        )
        result = await self.service.submit(app)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_submit_invalidated_approval(self):
        app = self.service.create_draft(
            user_id=str(uuid.uuid4()),
            service_id="income_certificate",
            form_data={"applicant_name": "Ravi"},
        )
        self.service.mark_ready_for_review(app)
        self.service.mark_awaiting_approval(app)
        app["approval_invalidated"] = True

        result = await self.service.submit(app)
        assert result["success"] is False
        assert "invalidated" in result["error"]


class TestApplicationTrackingService:
    def setup_method(self):
        self.tracking_service = ApplicationTrackingService()

    def test_register_adapter(self):
        class MockAdapter:
            async def track(self, ref):
                return {"status": "processing"}
            def normalize_status(self, s):
                return "processing"

        self.tracking_service.register_adapter("test_service", MockAdapter())
        assert self.tracking_service.get_adapter("test_service") is not None

    @pytest.mark.asyncio
    async def test_track_application(self):
        class MockAdapter:
            async def track(self, ref):
                return {"status": "under_review", "message": "Application is being reviewed"}
            def normalize_status(self, s):
                return "processing"

        self.tracking_service.register_adapter("income_certificate", MockAdapter())

        app = {
            "id": str(uuid.uuid4()),
            "service_id": "income_certificate",
            "reference_number": "REF-001",
            "status": "submitted",
        }
        result = await self.tracking_service.track_application(app)
        assert result["success"] is True
        assert result["normalized_status"] == "processing"
        assert result["status_changed"] is True

    @pytest.mark.asyncio
    async def test_track_no_reference(self):
        app = {
            "id": str(uuid.uuid4()),
            "service_id": "income_certificate",
            "reference_number": "",
            "status": "submitted",
        }
        result = await self.tracking_service.track_application(app)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_track_no_adapter(self):
        app = {
            "id": str(uuid.uuid4()),
            "service_id": "unknown_service",
            "reference_number": "REF-001",
            "status": "submitted",
        }
        result = await self.tracking_service.track_application(app)
        assert result["success"] is False

    def test_normalize_status(self):
        assert self.tracking_service.normalize_status("under_review") == "processing"
        assert self.tracking_service.normalize_status("issued") == "completed"
        assert self.tracking_service.normalize_status("returned for correction") == "action_required"

    def test_create_tracking_job(self):
        job = self.tracking_service.create_tracking_job(
            application_id=str(uuid.uuid4()),
            service_id="income_certificate",
            reference_number="REF-001",
        )
        assert job["job_id"]
        assert job["status"] == "scheduled"
