import pytest
from uuid import uuid4
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.jurisdiction import JurisdictionCreate, JurisdictionRead
from app.schemas.service import ServiceCreate, ServiceRead
from app.schemas.document import DocumentCreate, DocumentRead
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationTimelineRead
from app.schemas.workflow import WorkflowCreate, WorkflowRead
from app.schemas.agent_task import AgentTaskCreate, AgentTaskRead
from app.schemas.approval import ApprovalCreate, ApprovalRead
from app.schemas.grievance import GrievanceCreate, GrievanceRead
from app.schemas.audit_event import AuditEventCreate, AuditEventRead


class TestUserSchemas:
    def test_user_create(self):
        user = UserCreate(name="Test", email="test@test.com", phone="+911234567890")
        assert user.name == "Test"
        assert user.preferred_language == "en"

    def test_user_update_partial(self):
        update = UserUpdate(name="Updated")
        assert update.name == "Updated"
        assert update.email is None


class TestJurisdictionSchemas:
    def test_jurisdiction_create(self):
        j = JurisdictionCreate(code="KA-BLR", name="Bangalore", country="India", state="Karnataka")
        assert j.code == "KA-BLR"


class TestServiceSchemas:
    def test_service_create(self):
        svc = ServiceCreate(
            service_id="test",
            display_name="Test",
            description="Test service",
            department="Test Dept",
            official_portal="https://test.gov.in",
            adapter="mock",
        )
        assert svc.enabled is True
        assert svc.capabilities == []


class TestDocumentSchemas:
    def test_document_create(self):
        doc = DocumentCreate(
            user_id=uuid4(),
            document_type="aadhaar",
            file_name="test.pdf",
            storage_reference="/storage/test.pdf",
            mime_type="application/pdf",
            file_size=1024,
        )
        assert doc.document_type == "aadhaar"


class TestApplicationSchemas:
    def test_application_create(self):
        app = ApplicationCreate(user_id=uuid4(), service_id=uuid4())
        assert app.form_data == {}

    def test_timeline_read(self):
        tl = ApplicationTimelineRead(
            id=uuid4(),
            application_id=uuid4(),
            event_type="created",
            status="draft",
            timestamp="2026-08-22T00:00:00Z",
        )
        assert tl.event_type == "created"


class TestWorkflowSchemas:
    def test_workflow_create(self):
        wf = WorkflowCreate(service_id=uuid4(), workflow_version="1.0.0")
        assert wf.workflow_version == "1.0.0"


class TestAgentTaskSchemas:
    def test_agent_task_create(self):
        task = AgentTaskCreate(user_id=uuid4(), task_type="new_application")
        assert task.task_type == "new_application"


class TestApprovalSchemas:
    def test_approval_create(self):
        a = ApprovalCreate(user_id=uuid4(), action_type="submit_application")
        assert a.action_type == "submit_application"


class TestGrievanceSchemas:
    def test_grievance_create(self):
        g = GrievanceCreate(
            user_id=uuid4(),
            service_id=uuid4(),
            subject="Test",
            description="Test description",
        )
        assert g.subject == "Test"


class TestAuditEventSchemas:
    def test_audit_event_create(self):
        e = AuditEventCreate(event_type="agent_started")
        assert e.event_type == "agent_started"