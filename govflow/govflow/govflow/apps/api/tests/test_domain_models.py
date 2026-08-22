import pytest
from app.models.user import User, UserRole
from app.models.jurisdiction import Jurisdiction
from app.models.service import Service, ServiceCapability
from app.models.document import Document, DocumentType, DocumentStatus, OcrStatus
from app.models.application import Application, ApplicationStatus, ApplicationTimeline
from app.models.workflow import Workflow, WorkflowStatus
from app.models.agent_task import AgentTask, AgentTaskStatus, AgentTaskType
from app.models.approval import Approval, ApprovalStatus, ApprovalType
from app.models.grievance import Grievance, GrievanceStatus
from app.models.audit_event import AuditEvent, AuditEventType


class TestUserModel:
    def test_user_creation(self):
        user = User(name="Test User", email="test@example.com", phone="+911234567890")
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.preferred_language == "en"
        assert user.role == UserRole.CITIZEN.value

    def test_user_to_dict(self):
        user = User(name="Test", email="test@test.com")
        d = user.to_dict()
        assert d["name"] == "Test"
        assert d["email"] == "test@test.com"
        assert d["preferred_language"] == "en"

    def test_user_role_enum(self):
        assert UserRole.CITIZEN.value == "citizen"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.SUPPORT.value == "support"


class TestJurisdictionModel:
    def test_jurisdiction_creation(self):
        j = Jurisdiction(code="KA-BLR", name="Bangalore", country="India", state="Karnataka")
        assert j.code == "KA-BLR"
        assert j.country == "India"
        assert j.is_active is True

    def test_jurisdiction_to_dict(self):
        j = Jurisdiction(code="KA-BLR", name="Bangalore", country="India", state="Karnataka")
        d = j.to_dict()
        assert d["code"] == "KA-BLR"
        assert d["state"] == "Karnataka"


class TestServiceModel:
    def test_service_creation(self):
        svc = Service(
            service_id="income_cert",
            display_name="Income Certificate",
            description="Certifies income",
            department="Revenue",
            official_portal="https://test.gov.in",
            adapter="mock",
        )
        assert svc.service_id == "income_cert"
        assert svc.enabled is True
        assert svc.workflow_version == "1.0.0"

    def test_service_capability_enum(self):
        assert ServiceCapability.NEW_APPLICATION == "new_application"
        assert ServiceCapability.TRACK_APPLICATION == "track_application"
        assert ServiceCapability.RAISE_GRIEVANCE == "raise_grievance"


class TestDocumentModel:
    def test_document_creation(self):
        import uuid
        doc = Document(
            user_id=uuid.uuid4(),
            document_type="aadhaar",
            file_name="aadhaar.pdf",
            storage_reference="/storage/aadhaar.pdf",
            mime_type="application/pdf",
            file_size=1024,
        )
        assert doc.document_type == "aadhaar"
        assert doc.verification_status == DocumentStatus.PENDING
        assert doc.ocr_status == OcrStatus.NOT_PROCESSED

    def test_document_status_enum(self):
        assert DocumentStatus.PENDING == "pending"
        assert DocumentStatus.VERIFIED == "verified"
        assert DocumentStatus.REJECTED == "rejected"


class TestApplicationModel:
    def test_application_creation(self):
        import uuid
        app = Application(user_id=uuid.uuid4(), service_id=uuid.uuid4())
        assert app.status == ApplicationStatus.DRAFT
        assert app.form_data == {}

    def test_application_status_enum(self):
        assert ApplicationStatus.DRAFT == "draft"
        assert ApplicationStatus.SUBMITTED == "submitted"
        assert ApplicationStatus.COMPLETED == "completed"

    def test_timeline_creation(self):
        import uuid
        tl = ApplicationTimeline(application_id=uuid.uuid4(), event_type="created")
        assert tl.event_type == "created"


class TestWorkflowModel:
    def test_workflow_creation(self):
        import uuid
        wf = Workflow(service_id=uuid.uuid4(), workflow_version="1.0.0")
        assert wf.status == WorkflowStatus.DRAFT

    def test_workflow_status_enum(self):
        assert WorkflowStatus.ACTIVE == "active"
        assert WorkflowStatus.LEARNING == "learning"


class TestAgentTaskModel:
    def test_task_creation(self):
        import uuid
        task = AgentTask(user_id=uuid.uuid4())
        assert task.status == AgentTaskStatus.CREATED
        assert task.task_type == AgentTaskType.OTHER

    def test_task_status_enum(self):
        assert AgentTaskStatus.CREATED == "created"
        assert AgentTaskStatus.RUNNING == "running"
        assert AgentTaskStatus.COMPLETED == "completed"


class TestApprovalModel:
    def test_approval_creation(self):
        import uuid
        approval = Approval(user_id=uuid.uuid4(), action_type="submit_application")
        assert approval.status == ApprovalStatus.PENDING

    def test_approval_type_enum(self):
        assert ApprovalType.SUBMIT_APPLICATION == "submit_application"
        assert ApprovalType.MAKE_PAYMENT == "make_payment"


class TestGrievanceModel:
    def test_grievance_creation(self):
        import uuid
        g = Grievance(
            user_id=uuid.uuid4(),
            service_id=uuid.uuid4(),
            subject="Test",
            description="Test grievance",
        )
        assert g.status == GrievanceStatus.DRAFT


class TestAuditEventModel:
    def test_audit_event_creation(self):
        event = AuditEvent(event_type="agent_started")
        assert event.event_type == "agent_started"

    def test_audit_event_type_enum(self):
        assert AuditEventType.DOCUMENT_UPLOADED == "document_uploaded"
        assert AuditEventType.APPROVAL_GRANTED == "approval_granted"


class TestExtensibility:
    """Verify that two different mock services use the same generic schema."""

    def test_income_certificate_uses_generic_service(self):
        svc = Service(
            service_id="income_certificate",
            display_name="Income Certificate",
            description="Income cert",
            department="Revenue",
            official_portal="https://test.gov.in",
            adapter="mock_income",
            capabilities=["new_application", "track_application"],
            required_documents=[{"type": "income_proof", "mandatory": True}],
        )
        assert svc.service_id == "income_certificate"
        assert "new_application" in svc.capabilities

    def test_birth_certificate_uses_generic_service(self):
        svc = Service(
            service_id="birth_certificate",
            display_name="Birth Certificate",
            description="Birth cert",
            department="Health",
            official_portal="https://test.gov.in",
            adapter="mock_birth",
            capabilities=["new_application"],
            required_documents=[{"type": "hospital_record", "mandatory": True}],
        )
        assert svc.service_id == "birth_certificate"
        assert svc.adapter == "mock_birth"

    def test_no_separate_tables_needed(self):
        """Both services use the same 'services' table - no income_certificate_services table."""
        assert Service.__tablename__ == "services"