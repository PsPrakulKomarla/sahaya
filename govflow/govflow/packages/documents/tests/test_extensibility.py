import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.documents.base.ocr_provider import OCRProvider
from packages.documents.base.models import OCRResult, OCRPageResult
from packages.documents.document_service import DocumentService
from packages.documents.extraction.extractor import DefaultDocumentExtractor
from packages.documents.validation.validator import DefaultDocumentValidator
from packages.documents.storage.filesystem_storage import FilesystemStorage
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import ServiceMetadata, ServiceCapability, ServiceResponse, DocumentRequirement


class TestOCRExtensibility:
    """Test that OCR providers can be swapped without modifying DocumentService."""

    def test_mock_provider_implements_ocr_provider(self):
        from packages.documents.ocr.mock_provider import MockOCRProvider
        provider = MockOCRProvider()
        assert isinstance(provider, OCRProvider)

    def test_custom_ocr_provider(self):
        class CustomOCRProvider(OCRProvider):
            def provider_name(self):
                return "custom_ocr"

            def supported_languages(self):
                return ["en"]

            async def process(self, file_path, language=None):
                return OCRResult(
                    extracted_text="Custom OCR output",
                    pages=[OCRPageResult(page_number=1, text="Custom OCR output", confidence=0.99)],
                    overall_confidence=0.99,
                    language=language or "en",
                )

        provider = CustomOCRProvider()
        assert isinstance(provider, OCRProvider)
        assert provider.provider_name() == "custom_ocr"

    @pytest.mark.asyncio
    async def test_document_service_works_with_custom_provider(self):
        class CustomOCRProvider(OCRProvider):
            def provider_name(self):
                return "custom"

            def supported_languages(self):
                return ["en"]

            async def process(self, file_path, language=None):
                return OCRResult(
                    extracted_text="Name: Custom Name\nDOB: 01/01/2000",
                    overall_confidence=0.95,
                )

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            doc_service = DocumentService(
                CustomOCRProvider(),
                DefaultDocumentExtractor(),
                DefaultDocumentValidator(),
                storage,
            )
            ref = await storage.store(b"content", "test.pdf", "application/pdf", "user1")
            result = await doc_service.process_document(
                document_id="doc1",
                user_id="user1",
                storage_reference=ref,
                document_type="identity_proof",
                file_name="test.pdf",
            )
            assert result.confidence == 0.95
            assert len(result.extracted_fields) > 0


class TestServiceExtensibility:
    """Test that new services can be added without modifying the document engine."""

    def test_mock_passport_service_adapter(self):
        class MockPassportRenewalAdapter(GovernmentServiceAdapter):
            def metadata(self):
                return ServiceMetadata(
                    service_id="passport_renewal",
                    display_name="Passport Renewal",
                    description="Renew an expired or expiring passport",
                    department="Ministry of External Affairs",
                    jurisdiction="India",
                    official_portal="https://passportindia.gov.in",
                    capabilities=[
                        ServiceCapability.DOCUMENT_REQUIREMENTS,
                        ServiceCapability.NEW_APPLICATION,
                        ServiceCapability.TRACK_APPLICATION,
                    ],
                    required_documents=[
                        DocumentRequirement(
                            document_type="identity_proof",
                            display_name="Identity Proof",
                            description="Aadhaar Card or PAN Card",
                            mandatory=True,
                        ),
                        DocumentRequirement(
                            document_type="passport",
                            display_name="Current/Previous Passport",
                            description="Original passport for renewal",
                            mandatory=True,
                        ),
                        DocumentRequirement(
                            document_type="photograph",
                            display_name="Recent Photograph",
                            description="Recent passport size photograph",
                            mandatory=True,
                        ),
                    ],
                )

            async def discover(self, query, jurisdiction=None):
                return ServiceResponse(success=True, data={"service_id": "passport_renewal"})

        adapter = MockPassportRenewalAdapter()
        metadata = adapter.metadata()
        assert metadata.service_id == "passport_renewal"
        assert len(metadata.required_documents) == 3

        doc_types = [d.document_type for d in metadata.required_documents]
        assert "identity_proof" in doc_types
        assert "passport" in doc_types
        assert "photograph" in doc_types

    @pytest.mark.asyncio
    async def test_requirement_engine_with_new_service(self):
        from packages.services.registry.registry import ServiceRegistry
        from packages.documents.requirement_engine import DocumentRequirementEngine

        class MockPassportAdapter(GovernmentServiceAdapter):
            def metadata(self):
                return ServiceMetadata(
                    service_id="passport_renewal",
                    display_name="Passport Renewal",
                    description="Renew passport",
                    department="MEA",
                    jurisdiction="India",
                    official_portal="https://passportindia.gov.in",
                    capabilities=[ServiceCapability.DOCUMENT_REQUIREMENTS],
                    required_documents=[
                        DocumentRequirement(
                            document_type="identity_proof",
                            display_name="Identity Proof",
                            description="Aadhaar or PAN",
                            mandatory=True,
                        ),
                        DocumentRequirement(
                            document_type="passport",
                            display_name="Current Passport",
                            description="Existing passport",
                            mandatory=True,
                        ),
                    ],
                )

            async def discover(self, query, jurisdiction=None):
                return ServiceResponse(success=True, data={})

        registry = ServiceRegistry()
        registry.register_service(MockPassportAdapter())

        engine = DocumentRequirementEngine(registry=registry)
        result = await engine.get_requirements("passport_renewal")

        assert result.service_id == "passport_renewal"
        assert len(result.requirements) == 2
        req_types = [r.document_type for r in result.requirements]
        assert "identity_proof" in req_types
        assert "passport" in req_types

    @pytest.mark.asyncio
    async def test_document_matching_with_new_service(self):
        from packages.documents.matcher import DocumentMatcher

        matcher = DocumentMatcher()

        user_docs = [
            {"id": "doc1", "document_type": "aadhaar", "verification_status": "verified", "ocr_confidence": 0.95},
            {"id": "doc2", "document_type": "passport", "verification_status": "verified", "ocr_confidence": 0.9},
        ]

        required = [
            {"document_type": "identity_proof", "display_name": "Identity Proof", "mandatory": True},
            {"document_type": "passport", "display_name": "Passport", "mandatory": True},
            {"document_type": "photograph", "display_name": "Photograph", "mandatory": True},
        ]

        availability = matcher.check_availability(required, user_docs)
        assert len(availability) == 3
        assert availability[0].available is True
        assert availability[1].available is True
        assert availability[2].available is False

    @pytest.mark.asyncio
    async def test_full_pipeline_with_new_service(self):
        from packages.services.registry.registry import ServiceRegistry
        from packages.services.base.adapter import GovernmentServiceAdapter
        from packages.services.base.models import ServiceMetadata, ServiceCapability, ServiceResponse, DocumentRequirement

        class NewServiceAdapter(GovernmentServiceAdapter):
            def metadata(self):
                return ServiceMetadata(
                    service_id="new_mock_service",
                    display_name="New Mock Service",
                    description="A brand new service",
                    department="Test",
                    jurisdiction="Test",
                    official_portal="https://test.gov.in",
                    capabilities=[ServiceCapability.DOCUMENT_REQUIREMENTS, ServiceCapability.NEW_APPLICATION],
                    required_documents=[
                        DocumentRequirement(document_type="identity_proof", display_name="ID", description="ID doc", mandatory=True),
                    ],
                )

            async def discover(self, query, jurisdiction=None):
                return ServiceResponse(success=True, data={"service_id": "new_mock_service"})

        registry = ServiceRegistry()
        registry.register_service(NewServiceAdapter())

        from packages.documents.requirement_engine import DocumentRequirementEngine
        engine = DocumentRequirementEngine(registry=registry)
        reqs = await engine.get_requirements("new_mock_service")
        assert len(reqs.requirements) == 1

        from packages.documents.matcher import DocumentMatcher
        matcher = DocumentMatcher()
        user_docs = [{"id": "d1", "document_type": "aadhaar", "verification_status": "verified", "ocr_confidence": 0.9}]
        availability = matcher.check_availability(
            [{"document_type": r.document_type, "display_name": r.display_name, "mandatory": r.mandatory} for r in reqs.requirements],
            user_docs,
        )
        assert availability[0].available is True
