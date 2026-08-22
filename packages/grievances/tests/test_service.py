import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, AsyncMock
from packages.grievances.models import (
    Grievance,
    GrievanceStatus,
    GrievanceCategory,
    GrievanceFact,
    FactType,
    utcnow,
)
from packages.grievances.categories import GrievanceCategoryRegistry
from packages.grievances.composer import GrievanceComposer
from packages.grievances.ports import (
    GrievanceRepositoryPort,
    ApprovalPort,
    ServiceAdapterPort,
)
from packages.grievances.service import GrievanceService
from packages.grievances.errors import (
    GrievanceNotFound,
    GrievanceNotOwned,
    InvalidStateTransition,
    ApprovalRequired,
    ApprovalInvalidated,
    CapabilityUnsupportedError,
    AmbiguousApplication,
)
from packages.services.base.models import ServiceCapability
from packages.services.registry.registry import ServiceRegistry


class MockRepository(GrievanceRepositoryPort):
    def __init__(self):
        self._store = {}

    async def save(self, grievance: Grievance) -> Grievance:
        self._store[grievance.id] = grievance
        return grievance

    async def get(self, grievance_id) -> Grievance | None:
        return self._store.get(grievance_id)

    async def find_by_user(self, user_id) -> list[Grievance]:
        return [g for g in self._store.values() if g.user_id == user_id]

    async def find_by_application(self, application_id) -> list[Grievance]:
        return [g for g in self._store.values() if g.application_id == application_id]

    async def delete(self, grievance_id) -> bool:
        if grievance_id in self._store:
            del self._store[grievance_id]
            return True
        return False


class MockApprovalPort(ApprovalPort):
    def __init__(self):
        self._approvals = {}

    async def request_approval(self, user_id, action_type, summary, metadata) -> str:
        approval_id = f"approval_{len(self._approvals)}"
        self._approvals[approval_id] = {"status": "PENDING", "user_id": user_id}
        return approval_id

    async def is_approved(self, approval_id: str) -> bool:
        approval = self._approvals.get(approval_id)
        return approval and approval["status"] == "APPROVED"

    async def validate_approval(self, approval_id: str) -> bool:
        return await self.is_approved(approval_id)


class MockServiceAdapter:
    def __init__(self, service_id: str, supports_grievance: bool = True):
        self._service_id = service_id
        self._supports_grievance = supports_grievance

    def metadata(self):
        class Meta:
            service_id = self._service_id
            display_name = "Income Certificate"
            description = "Income certificate service"
            department = "Revenue Department"
            jurisdiction = "Karnataka"
            official_portal = "https://example.gov.in"
            enabled = True
            supported_languages = ["en", "kn", "hi"]
            workflow_version = "1.0.0"
        return Meta()

    def get_capabilities(self):
        caps = [ServiceCapability.DISCOVER, ServiceCapability.NEW_APPLICATION]
        if self._supports_grievance:
            caps.append(ServiceCapability.RAISE_GRIEVANCE)
        return caps

    def supports_capability(self, cap: ServiceCapability) -> bool:
        return cap in self.get_capabilities()

    async def raise_grievance(self, grievance, browser_agent, safety_policy):
        class Result:
            official_reference_number = "GRIEVANCE_REF_123"
            source_status = "registered"
            submitted_at = utcnow()
        return Result()


class TestGrievanceService:
    def setup_method(self):
        self.repo = MockRepository()
        self.approval = MockApprovalPort()
        self.registry = ServiceRegistry()
        self.adapter = MockServiceAdapter("income_certificate")
        self.registry.register_service(self.adapter)
        self.categories = GrievanceCategoryRegistry()
        self.composer = GrievanceComposer()

        self.service = GrievanceService(
            repository=self.repo,
            approval_port=self.approval,
            service_registry=self.registry,
            category_registry=self.categories,
            composer=self.composer,
        )

    @pytest.mark.asyncio
    async def test_create_draft(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="My application has been pending for two months",
            language="en",
        )
        assert grievance.user_id == user_id
        assert grievance.service_id == "income_certificate"
        assert grievance.category == GrievanceCategory.APPLICATION_DELAY
        assert grievance.status == GrievanceStatus.DRAFT

    @pytest.mark.asyncio
    async def test_create_draft_kannada(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="ನನ್ನ ಅರ್ಜಿ ಎರಡು ತಿಂಗಳು ಬಾಕಿ",
            language="kn",
        )
        assert grievance.category == GrievanceCategory.APPLICATION_DELAY

    @pytest.mark.asyncio
    async def test_create_draft_hindi(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="मेरा आवेदन दो महीने से लंबित है",
            language="hi",
        )
        assert grievance.category == GrievanceCategory.APPLICATION_DELAY

    @pytest.mark.asyncio
    async def test_create_draft_service_not_found(self):
        user_id = uuid4()
        with pytest.raises(ValueError, match="not found"):
            await self.service.create_draft(
                user_id=user_id,
                service_id="nonexistent",
                user_issue="Test",
            )

    @pytest.mark.asyncio
    async def test_create_draft_unsupported_capability(self):
        adapter = MockServiceAdapter("no_grievance", supports_grievance=False)
        self.registry.register_service(adapter)
        user_id = uuid4()
        with pytest.raises(CapabilityUnsupportedError):
            await self.service.create_draft(
                user_id=user_id,
                service_id="no_grievance",
                user_issue="Test",
            )

    @pytest.mark.asyncio
    async def test_link_application(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        app_id = uuid4()
        updated = await self.service.link_application(grievance.id, user_id, app_id)
        assert updated.application_id == app_id

    @pytest.mark.asyncio
    async def test_link_application_not_owned(self):
        user_id1 = uuid4()
        user_id2 = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id1,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        with pytest.raises(GrievanceNotOwned):
            await self.service.link_application(grievance.id, user_id2, uuid4())

    @pytest.mark.asyncio
    async def test_update_draft(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        updated = await self.service.update_draft(
            grievance.id,
            user_id,
            subject="Updated Subject",
            description="Updated description",
        )
        assert updated.subject == "Updated Subject"
        assert updated.description == "Updated description"
        assert updated.status == GrievanceStatus.PREPARING

    @pytest.mark.asyncio
    async def test_update_draft_wrong_state(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        grievance.status = GrievanceStatus.SUBMITTED
        await self.repo.save(grievance)

        with pytest.raises(InvalidStateTransition):
            await self.service.update_draft(grievance.id, user_id, subject="New")

    @pytest.mark.asyncio
    async def test_prepare_for_review(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        updated = await self.service.prepare_for_review(grievance.id, user_id)
        assert updated.status == GrievanceStatus.READY_FOR_REVIEW

    @pytest.mark.asyncio
    async def test_request_approval(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        await self.service.prepare_for_review(grievance.id, user_id)
        updated, approval_id = await self.service.request_approval(grievance.id, user_id)
        assert updated.status == GrievanceStatus.AWAITING_APPROVAL
        assert approval_id is not None
        assert updated.approval_fingerprint is not None

    @pytest.mark.asyncio
    async def test_grant_approval(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        await self.service.prepare_for_review(grievance.id, user_id)
        updated, approval_id = await self.service.request_approval(grievance.id, user_id)

        # Mock approval as approved
        self.approval._approvals[approval_id]["status"] = "APPROVED"

        granted = await self.service.grant_approval(grievance.id, approval_id, user_id)
        assert granted.status == GrievanceStatus.SUBMITTED

    @pytest.mark.asyncio
    async def test_grant_approval_invalid_fingerprint(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        await self.service.prepare_for_review(grievance.id, user_id)
        updated, approval_id = await self.service.request_approval(grievance.id, user_id)

        # Modify grievance to invalidate fingerprint
        grievance.subject = "Changed"
        await self.repo.save(grievance)
        self.approval._approvals[approval_id]["status"] = "APPROVED"

        with pytest.raises(ApprovalInvalidated):
            await self.service.grant_approval(grievance.id, approval_id, user_id)

    @pytest.mark.asyncio
    async def test_reject_approval(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        await self.service.prepare_for_review(grievance.id, user_id)
        updated, approval_id = await self.service.request_approval(grievance.id, user_id)

        rejected = await self.service.reject_approval(grievance.id, approval_id)
        assert rejected.status == GrievanceStatus.READY_FOR_REVIEW
        assert rejected.approval_id is None

    @pytest.mark.asyncio
    async def test_get_grievance(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        fetched = await self.service.get_grievance(grievance.id, user_id)
        assert fetched.id == grievance.id

    @pytest.mark.asyncio
    async def test_get_grievance_not_owned(self):
        user_id1 = uuid4()
        user_id2 = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id1,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        with pytest.raises(GrievanceNotOwned):
            await self.service.get_grievance(grievance.id, user_id2)

    @pytest.mark.asyncio
    async def test_list_grievances(self):
        user_id = uuid4()
        await self.service.create_draft(user_id, "income_certificate", "Issue 1")
        await self.service.create_draft(user_id, "income_certificate", "Issue 2")
        grievances = await self.service.list_grievances(user_id)
        assert len(grievances) == 2

    @pytest.mark.asyncio
    async def test_cancel_grievance(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        cancelled = await self.service.cancel_grievance(grievance.id, user_id)
        assert cancelled.status == GrievanceStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_grievance_invalid_state(self):
        user_id = uuid4()
        grievance = await self.service.create_draft(
            user_id=user_id,
            service_id="income_certificate",
            user_issue="Test issue",
        )
        grievance.status = GrievanceStatus.RESOLVED
        await self.repo.save(grievance)

        with pytest.raises(InvalidStateTransition):
            await self.service.cancel_grievance(grievance.id, user_id)

    @pytest.mark.asyncio
    async def test_detect_category(self):
        cat = await self.service.detect_category("My application is delayed", "en")
        assert cat == GrievanceCategory.APPLICATION_DELAY