import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock
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
from packages.grievances.ports import GrievanceRepositoryPort, ApprovalPort
from packages.grievances.service import GrievanceService
from packages.grievances.tracking import GrievanceTrackingService
from packages.grievances.ports import GrievanceTrackingAdapter
from packages.services.registry.registry import ServiceRegistry, get_registry, reset_registry
from packages.services.base.models import ServiceCapability


class MockRepo(GrievanceRepositoryPort):
    def __init__(self):
        self._store = {}
    async def save(self, g): self._store[g.id] = g; return g
    async def get(self, id): return self._store.get(id)
    async def find_by_user(self, uid): return [g for g in self._store.values() if g.user_id == uid]
    async def find_by_application(self, aid): return [g for g in self._store.values() if g.application_id == aid]
    async def delete(self, id): return False


class MockApproval(ApprovalPort):
    def __init__(self):
        self._approvals = {}
    async def request_approval(self, user_id, action_type, summary, metadata):
        aid = f"approval_{len(self._approvals)}"
        self._approvals[aid] = {"status": "PENDING", "user_id": user_id}
        return aid
    async def is_approved(self, aid): return self._approvals.get(aid, {}).get("status") == "APPROVED"
    async def validate_approval(self, aid): return await self.is_approved(aid)


class MockAdapter:
    def __init__(self, service_id: str):
        self._service_id = service_id
    def metadata(self):
        class M:
            service_id = "income_certificate"
            display_name = "Income Certificate"
            description = "Income certificate service"
            department = "Revenue Department"
            jurisdiction = "Karnataka"
            official_portal = "https://example.gov.in"
            enabled = True
            supported_languages = ["en", "kn", "hi"]
            workflow_version = "1.0.0"
            aliases = ["income certificate", "income cert"]
            capabilities = [ServiceCapability.DISCOVER, ServiceCapability.NEW_APPLICATION, ServiceCapability.RAISE_GRIEVANCE]
            estimated_processing_time = "7 days"
            fees = "Rs. 50"
        return M()
    def get_capabilities(self):
        return [ServiceCapability.DISCOVER, ServiceCapability.NEW_APPLICATION, ServiceCapability.RAISE_GRIEVANCE]
    async def raise_grievance(self, grievance, browser_agent, safety_policy):
        class Result:
            official_reference_number = "GRIEVANCE_REF_123"
            source_status = "registered"
            submitted_at = utcnow()
        return Result()


class MockTrackingAdapter(GrievanceTrackingAdapter):
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


class TestEndToEndGrievanceFlow:
    @pytest.mark.asyncio
    async def test_full_grievance_lifecycle_english(self):
        """Test: USER MESSAGE -> LANGUAGE DETECTION -> INTENT -> SERVICE RESOLUTION -> APPLICATION MATCH -> GRIEVANCE DRAFT -> USER REVIEW -> APPROVAL -> MOCK SUBMISSION -> REFERENCE -> TRACKING"""
        repo = MockRepo()
        approval = MockApproval()
        reset_registry()
        registry = get_registry()
        adapter = MockAdapter("income_certificate")
        registry.register_service(adapter)
        categories = GrievanceCategoryRegistry()
        composer = GrievanceComposer()

        service = GrievanceService(
            repository=repo,
            approval_port=approval,
            service_registry=registry,
            category_registry=categories,
            composer=composer,
        )

        user_id = uuid4()

        # 1. USER MESSAGE (English)
        user_message = "My income certificate application has been pending for two months"

        # 2. LANGUAGE DETECTION
        from packages.services.intent import RuleBasedLanguageDetector
        detector = RuleBasedLanguageDetector()
        language, confidence = detector.detect(user_message)
        assert language.value == "en"

        # 3. INTENT (using intent engine)
        from packages.services.intent import RuleBasedIntentEngine
        engine = RuleBasedIntentEngine(language_detector=detector)
        intent = engine.parse(user_message)
        assert intent.intent == "RAISE_GRIEVANCE"

        # 4. SERVICE RESOLUTION
        from packages.services.registry import ServiceResolver
        resolver = ServiceResolver()
        resolution = await resolver.resolve_intent(intent)
        assert resolution.service_id == "income_certificate"

        # 5. APPLICATION MATCH (simulated - user has one application)
        app_id = uuid4()

        # 6. GRIEVANCE DRAFT
        grievance = await service.create_draft(
            user_id=user_id,
            service_id=resolution.service_id,
            user_issue=user_message,
            language=language.value,
            application_id=app_id,
        )
        assert grievance.category == GrievanceCategory.APPLICATION_DELAY
        assert grievance.status == GrievanceStatus.DRAFT

        # Link application
        grievance = await service.link_application(grievance.id, user_id, app_id)
        assert grievance.application_id == app_id

        # 7. USER REVIEW (prepare for review)
        grievance = await service.prepare_for_review(grievance.id, user_id)
        assert grievance.status == GrievanceStatus.READY_FOR_REVIEW

        # 8. APPROVAL
        grievance, approval_id = await service.request_approval(grievance.id, user_id)
        assert grievance.status == GrievanceStatus.AWAITING_APPROVAL

        # Simulate user approval
        approval._approvals[approval_id]["status"] = "APPROVED"
        grievance = await service.grant_approval(grievance.id, approval_id, user_id)
        assert grievance.status == GrievanceStatus.SUBMITTED

        # 9. MOCK SUBMISSION
        class MockBrowser:
            pass
        class MockSafety:
            pass

        grievance = await service.submit(grievance.id, MockBrowser(), MockSafety())
        assert grievance.official_reference_number == "GRIEVANCE_REF_123"
        assert grievance.status == GrievanceStatus.PROCESSING

        # 10. REFERENCE
        assert grievance.official_reference_number is not None

        # 11. TRACKING
        tracking_adapter = MockTrackingAdapter(["registered", "under examination", "resolved"])
        service._tracking.set_adapter(tracking_adapter)

        # First track - portal returns "registered" which normalizes to SUBMITTED
        grievance, result = await service.track(grievance.id, user_id)
        assert result.normalized_status == GrievanceStatus.SUBMITTED
        assert result.source_status == "registered"

        # Second track - portal returns "under examination" which normalizes to PROCESSING
        grievance, result = await service.track(grievance.id, user_id)
        assert result.normalized_status == GrievanceStatus.PROCESSING
        assert result.source_status == "under examination"

        # Third track - portal returns "resolved" which normalizes to RESOLVED
        grievance, result = await service.track(grievance.id, user_id)
        assert result.normalized_status == GrievanceStatus.RESOLVED
        assert result.source_status == "resolved"
        assert grievance.completed_at is not None

    @pytest.mark.asyncio
    async def test_full_grievance_lifecycle_kannada(self):
        repo = MockRepo()
        approval = MockApproval()
        reset_registry()
        registry = get_registry()
        adapter = MockAdapter("income_certificate")
        registry.register_service(adapter)
        categories = GrievanceCategoryRegistry()
        composer = GrievanceComposer()

        service = GrievanceService(
            repository=repo,
            approval_port=approval,
            service_registry=registry,
            category_registry=categories,
            composer=composer,
        )

        user_id = uuid4()

        # USER MESSAGE (Kannada)
        user_message = "ನನ್ನ ಆದಾಯ ಹಣದ ದಾಖಲೆ ಅರ್ಜಿ ಎರಡು ತಿಂಗಳು ಬಾಕಿ"

        # LANGUAGE DETECTION
        from packages.services.intent import RuleBasedLanguageDetector
        detector = RuleBasedLanguageDetector()
        language, confidence = detector.detect(user_message)
        assert language.value == "kn"

        # INTENT
        from packages.services.intent import RuleBasedIntentEngine
        engine = RuleBasedIntentEngine(language_detector=detector)
        intent = engine.parse(user_message)
        assert intent.intent == "RAISE_GRIEVANCE"

        # SERVICE RESOLUTION
        from packages.services.registry import ServiceResolver
        resolver = ServiceResolver()
        resolution = await resolver.resolve_intent(intent)
        assert resolution.service_id == "income_certificate"

        # GRIEVANCE DRAFT
        grievance = await service.create_draft(
            user_id=user_id,
            service_id=resolution.service_id,
            user_issue=user_message,
            language=language.value,
        )
        assert grievance.category == GrievanceCategory.APPLICATION_DELAY

        # Complete flow...
        await service.prepare_for_review(grievance.id, user_id)
        _, approval_id = await service.request_approval(grievance.id, user_id)
        approval._approvals[approval_id]["status"] = "APPROVED"
        grievance = await service.grant_approval(grievance.id, approval_id, user_id)

        class MockBrowser: pass
        class MockSafety: pass
        grievance = await service.submit(grievance.id, MockBrowser(), MockSafety())
        assert grievance.status == GrievanceStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_full_grievance_lifecycle_hindi(self):
        repo = MockRepo()
        approval = MockApproval()
        reset_registry()
        registry = get_registry()
        adapter = MockAdapter("income_certificate")
        registry.register_service(adapter)
        categories = GrievanceCategoryRegistry()
        composer = GrievanceComposer()

        service = GrievanceService(
            repository=repo,
            approval_port=approval,
            service_registry=registry,
            category_registry=categories,
            composer=composer,
        )

        user_id = uuid4()

        # USER MESSAGE (Hindi)
        user_message = "मेरा आय प्रमाण पत्र आवेदन दो महीने से लंबित है"

        # LANGUAGE DETECTION
        from packages.services.intent import RuleBasedLanguageDetector
        detector = RuleBasedLanguageDetector()
        language, confidence = detector.detect(user_message)
        assert language.value == "hi"

        # INTENT
        from packages.services.intent import RuleBasedIntentEngine
        engine = RuleBasedIntentEngine(language_detector=detector)
        intent = engine.parse(user_message)
        assert intent.intent == "RAISE_GRIEVANCE"

        # SERVICE RESOLUTION
        from packages.services.registry import ServiceResolver
        resolver = ServiceResolver()
        resolution = await resolver.resolve_intent(intent)
        assert resolution.service_id == "income_certificate"

        # GRIEVANCE DRAFT
        grievance = await service.create_draft(
            user_id=user_id,
            service_id=resolution.service_id,
            user_issue=user_message,
            language=language.value,
        )
        assert grievance.category == GrievanceCategory.APPLICATION_DELAY

        # Complete flow...
        await service.prepare_for_review(grievance.id, user_id)
        _, approval_id = await service.request_approval(grievance.id, user_id)
        approval._approvals[approval_id]["status"] = "APPROVED"
        grievance = await service.grant_approval(grievance.id, approval_id, user_id)

        class MockBrowser: pass
        class MockSafety: pass
        grievance = await service.submit(grievance.id, MockBrowser(), MockSafety())
        assert grievance.status == GrievanceStatus.PROCESSING