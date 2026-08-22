import os
import sys
import pytest
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.documents.matcher import DocumentMatcher
from packages.documents.requirement_engine import DocumentRequirementEngine
from packages.documents.base.models import ExtractedField, FieldSource, ExpiryStatus


class TestDocumentMatcher:
    def setup_method(self):
        self.matcher = DocumentMatcher()

    def test_match_exact_type(self):
        user_docs = [{"id": "doc1", "document_type": "aadhaar", "verification_status": "verified", "ocr_confidence": 0.95}]
        result = self.matcher.match_documents("identity_proof", user_docs)
        assert result.matched is True
        assert result.document_id == "doc1"

    def test_match_compatible_type(self):
        user_docs = [{"id": "doc1", "document_type": "pan", "verification_status": "verified", "ocr_confidence": 0.9}]
        result = self.matcher.match_documents("identity_proof", user_docs)
        assert result.matched is True

    def test_no_match(self):
        user_docs = [{"id": "doc1", "document_type": "income_proof", "verification_status": "verified"}]
        result = self.matcher.match_documents("identity_proof", user_docs)
        assert result.matched is False

    def test_match_score_verified_higher(self):
        user_docs = [
            {"id": "doc1", "document_type": "aadhaar", "verification_status": "verified", "ocr_confidence": 0.95},
            {"id": "doc2", "document_type": "aadhaar", "verification_status": "pending", "ocr_confidence": 0.9},
        ]
        result = self.matcher.match_documents("identity_proof", user_docs)
        assert result.document_id == "doc1"

    def test_check_availability(self):
        required = [
            {"document_type": "identity_proof", "display_name": "Identity Proof", "mandatory": True},
            {"document_type": "income_proof", "display_name": "Income Proof", "mandatory": True},
        ]
        user_docs = [
            {"id": "doc1", "document_type": "aadhaar", "verification_status": "verified", "ocr_confidence": 0.9},
        ]
        results = self.matcher.check_availability(required, user_docs)
        assert len(results) == 2
        assert results[0].available is True
        assert results[1].available is False

    def test_check_cross_document_consistent(self):
        fields_doc1 = [ExtractedField(field="name", value="Ravi Kumar", confidence=0.9, verified=True)]
        fields_doc2 = [ExtractedField(field="name", value="Ravi Kumar", confidence=0.9, verified=True)]
        result = self.matcher.check_cross_document_consistency([fields_doc1, fields_doc2])
        assert result.consistent is True

    def test_check_cross_document_inconsistent(self):
        fields_doc1 = [ExtractedField(field="name", value="Ravi Kumar", confidence=0.9, verified=True)]
        fields_doc2 = [ExtractedField(field="name", value="Ravi K.", confidence=0.9, verified=True)]
        result = self.matcher.check_cross_document_consistency([fields_doc1, fields_doc2])
        assert result.consistent is False
        assert len(result.discrepancies) == 1

    def test_expiry_check_valid(self):
        doc = {"expires_at": "2099-12-31T00:00:00+00:00"}
        status = self.matcher._check_expiry(doc)
        assert status == ExpiryStatus.VALID

    def test_expiry_check_expired(self):
        doc = {"expires_at": "2020-01-01T00:00:00+00:00"}
        status = self.matcher._check_expiry(doc)
        assert status == ExpiryStatus.EXPIRED

    def test_expiry_check_unknown(self):
        doc = {}
        status = self.matcher._check_expiry(doc)
        assert status == ExpiryStatus.UNKNOWN


class TestDocumentRequirementEngine:
    @pytest.mark.asyncio
    async def test_get_requirements_income_certificate(self):
        from packages.services.registry.registry import ServiceRegistry
        from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter

        registry = ServiceRegistry()
        registry.register_service(MockIncomeCertificateAdapter())

        engine = DocumentRequirementEngine(registry=registry)
        result = await engine.get_requirements("income_certificate", "new_application")

        assert result.service_id == "income_certificate"
        assert len(result.requirements) > 0
        req_types = [r.document_type for r in result.requirements]
        assert "identity_proof" in req_types

    @pytest.mark.asyncio
    async def test_get_requirements_unknown_service(self):
        from packages.services.registry.registry import ServiceRegistry

        registry = ServiceRegistry()
        engine = DocumentRequirementEngine(registry=registry)
        result = await engine.get_requirements("unknown_service")

        assert result.service_id == "unknown_service"
        assert len(result.requirements) == 0
