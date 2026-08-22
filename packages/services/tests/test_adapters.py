import pytest
from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter
from packages.services.adapters.birth_certificate.adapter import MockBirthCertificateAdapter
from packages.services.base.models import ServiceCapability


class TestMockIncomeCertificateAdapter:
    @pytest.fixture
    def adapter(self):
        return MockIncomeCertificateAdapter()

    def test_metadata(self, adapter):
        metadata = adapter.metadata()
        assert metadata.service_id == "income_certificate"
        assert metadata.display_name == "Income Certificate"
        assert metadata.department == "Revenue Department"
        assert metadata.jurisdiction == "Karnataka"

    def test_capabilities(self, adapter):
        caps = adapter.get_capabilities()
        assert ServiceCapability.DISCOVER in caps
        assert ServiceCapability.ELIGIBILITY_CHECK in caps
        assert ServiceCapability.NEW_APPLICATION in caps
        assert ServiceCapability.TRACK_APPLICATION in caps
        assert ServiceCapability.RAISE_GRIEVANCE in caps

    def test_supports_capability(self, adapter):
        assert adapter.supports_capability(ServiceCapability.NEW_APPLICATION) is True
        assert adapter.supports_capability(ServiceCapability.UPDATE_RECORD) is False

    @pytest.mark.asyncio
    async def test_discover(self, adapter):
        result = await adapter.discover("income certificate")
        assert result.success is True
        assert result.data["service_id"] == "income_certificate"

    @pytest.mark.asyncio
    async def test_check_eligibility(self, adapter):
        result = await adapter.check_eligibility({
            "age": 25,
            "is_resident": True,
            "annual_income": 500000,
        })
        assert result.success is True
        assert result.data["eligible"] is True

    @pytest.mark.asyncio
    async def test_check_eligibility_not_resident(self, adapter):
        result = await adapter.check_eligibility({
            "age": 25,
            "is_resident": False,
            "annual_income": 500000,
        })
        assert result.success is True
        assert result.data["eligible"] is False

    @pytest.mark.asyncio
    async def test_create_application(self, adapter):
        result = await adapter.create_application({
            "full_name": "Test User",
            "father_name": "Test Father",
            "address": "Test Address",
            "income": 500000,
        })
        assert result.success is True
        assert "application_id" in result.data

    @pytest.mark.asyncio
    async def test_create_application_missing_fields(self, adapter):
        result = await adapter.create_application({"full_name": "Test"})
        assert result.success is False
        assert result.error.error_code == "MISSING_FIELDS"

    @pytest.mark.asyncio
    async def test_track_application(self, adapter):
        result = await adapter.track_application("MOCK-REF-001")
        assert result.success is True
        assert result.data["status"] == "under_review"

    @pytest.mark.asyncio
    async def test_workflow_plan(self, adapter):
        result = await adapter.get_workflow_plan("new_application")
        assert result.success is True
        assert len(result.data["steps"]) == 7
        assert result.data["steps"][4]["requires_human_approval"] is True


class TestMockBirthCertificateAdapter:
    @pytest.fixture
    def adapter(self):
        return MockBirthCertificateAdapter()

    def test_metadata(self, adapter):
        metadata = adapter.metadata()
        assert metadata.service_id == "birth_certificate"
        assert metadata.display_name == "Birth Certificate"

    def test_capabilities(self, adapter):
        caps = adapter.get_capabilities()
        assert ServiceCapability.NEW_APPLICATION in caps
        assert ServiceCapability.UPDATE_RECORD not in caps

    @pytest.mark.asyncio
    async def test_create_application(self, adapter):
        result = await adapter.create_application({
            "child_name": "Test Child",
            "birth_date": "2026-01-01",
            "birth_place": "Bangalore",
            "parents_names": "Parent 1, Parent 2",
        })
        assert result.success is True
        assert "application_id" in result.data

    @pytest.mark.asyncio
    async def test_create_application_missing_fields(self, adapter):
        result = await adapter.create_application({"child_name": "Test"})
        assert result.success is False


class TestExtensibility:
    """Test that adding a new service does not require modifying core agent code."""

    def test_new_service_can_be_registered(self):
        from packages.services.registry.registry import ServiceRegistry
        from packages.services.base.adapter import GovernmentServiceAdapter
        from packages.services.base.models import ServiceMetadata, ServiceCapability, ServiceResponse

        class MockNewServiceAdapter(GovernmentServiceAdapter):
            def metadata(self):
                return ServiceMetadata(
                    service_id="new_mock_service",
                    display_name="New Mock Service",
                    description="A new mock service",
                    department="Test Dept",
                    jurisdiction="Test State",
                    official_portal="https://test.gov.in",
                    capabilities=[ServiceCapability.DISCOVER, ServiceCapability.NEW_APPLICATION],
                )

            async def discover(self, query, jurisdiction=None):
                return ServiceResponse(success=True, data={"service_id": "new_mock_service"})

        registry = ServiceRegistry()
        registry.register_service(MockNewServiceAdapter())

        services = registry.list_services()
        assert len(services) == 1
        assert services[0].service_id == "new_mock_service"

        adapter = registry.get_service("new_mock_service")
        assert adapter is not None
        assert ServiceCapability.NEW_APPLICATION in adapter.get_capabilities()