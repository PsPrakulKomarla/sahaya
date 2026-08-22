import pytest
from packages.services.registry.registry import ServiceRegistry, get_registry, reset_registry
from packages.services.registry.resolver import ServiceResolver
from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter
from packages.services.adapters.birth_certificate.adapter import MockBirthCertificateAdapter
from packages.services.base.models import ServiceCapability


@pytest.fixture
def registry():
    reg = reset_registry()
    reg.register_service(MockIncomeCertificateAdapter())
    reg.register_service(MockBirthCertificateAdapter())
    return reg


class TestServiceRegistry:
    def test_register_service(self, registry):
        services = registry.list_services()
        assert len(services) == 2

    def test_get_service(self, registry):
        adapter = registry.get_service("income_certificate")
        assert adapter is not None
        assert adapter.metadata().service_id == "income_certificate"

    def test_get_service_not_found(self, registry):
        adapter = registry.get_service("nonexistent_service")
        assert adapter is None

    def test_list_services(self, registry):
        services = registry.list_services()
        ids = [s.service_id for s in services]
        assert "income_certificate" in ids
        assert "birth_certificate" in ids

    def test_find_services(self, registry):
        results = registry.find_services("income")
        assert len(results) == 1
        assert results[0].metadata().service_id == "income_certificate"

    def test_find_services_by_department(self, registry):
        results = registry.find_services("Revenue")
        assert len(results) == 1

    def test_find_by_capability(self, registry):
        results = registry.find_by_capability(ServiceCapability.ELIGIBILITY_CHECK)
        assert len(results) == 1
        assert results[0].metadata().service_id == "income_certificate"

    def test_find_by_jurisdiction(self, registry):
        results = registry.find_by_jurisdiction("Karnataka")
        assert len(results) == 2

    def test_get_capabilities(self, registry):
        caps = registry.get_capabilities("income_certificate")
        assert ServiceCapability.NEW_APPLICATION in caps
        assert ServiceCapability.TRACK_APPLICATION in caps

    def test_validate_service(self, registry):
        assert registry.validate_service("income_certificate") is True
        assert registry.validate_service("nonexistent") is False

    def test_clear(self, registry):
        registry.clear()
        assert len(registry.list_services()) == 0


class TestServiceResolver:
    @pytest.fixture
    def resolver(self, registry):
        return ServiceResolver()

    @pytest.mark.asyncio
    async def test_resolve_income_certificate(self, resolver):
        result = await resolver.resolve("income certificate")
        assert result.success is True
        assert result.data["service_id"] == "income_certificate"

    @pytest.mark.asyncio
    async def test_resolve_not_found(self, resolver):
        result = await resolver.resolve("nonexistent service")
        assert result.success is False
        assert result.error.error_code == "SERVICE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_resolve_with_jurisdiction(self, resolver):
        result = await resolver.resolve("income certificate", jurisdiction="Karnataka")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_resolve_wrong_jurisdiction(self, resolver):
        result = await resolver.resolve("income certificate", jurisdiction="Maharashtra")
        assert result.success is False
        assert result.error.error_code == "JURISDICTION_NOT_AVAILABLE"

    @pytest.mark.asyncio
    async def test_get_workflow_plan(self, resolver):
        result = await resolver.get_workflow_plan("income_certificate", "new_application")
        assert result.success is True
        assert "steps" in result.data
        assert len(result.data["steps"]) > 0

    @pytest.mark.asyncio
    async def test_get_workflow_plan_not_found(self, resolver):
        result = await resolver.get_workflow_plan("nonexistent", "new_application")
        assert result.success is False