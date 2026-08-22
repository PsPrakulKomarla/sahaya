import pytest
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import (
    ServiceCapability,
    ServiceMetadata,
    ServiceResponse,
    CapabilityNotSupportedError,
    DocumentRequirement,
)


class TestServiceCapability:
    def test_capability_enum_values(self):
        assert ServiceCapability.DISCOVER.value == "discover"
        assert ServiceCapability.NEW_APPLICATION.value == "new_application"
        assert ServiceCapability.TRACK_APPLICATION.value == "track_application"

    def test_capability_from_string(self):
        cap = ServiceCapability("eligibility_check")
        assert cap == ServiceCapability.ELIGIBILITY_CHECK


class TestServiceMetadata:
    def test_metadata_creation(self):
        metadata = ServiceMetadata(
            service_id="test_service",
            display_name="Test Service",
            description="A test service",
            department="Test Department",
            jurisdiction="Test Jurisdiction",
            official_portal="https://test.gov.in",
        )
        assert metadata.service_id == "test_service"
        assert metadata.enabled is True
        assert metadata.supported_languages == ["en"]

    def test_metadata_with_documents(self):
        doc = DocumentRequirement(
            document_type="identity_proof",
            display_name="Identity Proof",
            description="Aadhaar or PAN",
            mandatory=True,
        )
        metadata = ServiceMetadata(
            service_id="test",
            display_name="Test",
            description="Test",
            department="Test",
            jurisdiction="Test",
            official_portal="https://test.gov.in",
            required_documents=[doc],
        )
        assert len(metadata.required_documents) == 1
        assert metadata.required_documents[0].mandatory is True


class TestServiceResponse:
    def test_success_response(self):
        resp = ServiceResponse(success=True, data={"key": "value"})
        assert resp.success is True
        assert resp.data == {"key": "value"}
        assert resp.error is None

    def test_error_response(self):
        from packages.services.base.models import ServiceError
        error = ServiceError(error_code="TEST_ERROR", message="Test error")
        resp = ServiceResponse(success=False, error=error)
        assert resp.success is False
        assert resp.error.error_code == "TEST_ERROR"