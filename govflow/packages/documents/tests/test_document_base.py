import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.documents.base.models import (
    CrossDocumentCheckResult,
    DocumentMatchResult,
    DocumentPipelineStatus,
    DocumentType,
    DocumentValidationResult,
    ExpiryStatus,
    ExtractedField,
    FieldSource,
    OCRPageResult,
    OCRResult,
    RequiredDocumentsResult,
)


class TestDocumentBaseModels:
    def test_document_type_enum(self):
        assert DocumentType.IDENTITY_PROOF == "identity_proof"
        assert DocumentType.ADDRESS_PROOF == "address_proof"
        assert DocumentType.INCOME_PROOF == "income_proof"
        assert DocumentType.PASSPORT == "passport"
        assert DocumentType.OTHER == "other"

    def test_pipeline_status_enum(self):
        assert DocumentPipelineStatus.UPLOADED == "uploaded"
        assert DocumentPipelineStatus.OCR_PROCESSING == "ocr_processing"
        assert DocumentPipelineStatus.VERIFIED == "verified"
        assert DocumentPipelineStatus.REJECTED == "rejected"
        assert DocumentPipelineStatus.FAILED == "failed"

    def test_field_source_enum(self):
        assert FieldSource.OCR == "ocr"
        assert FieldSource.USER_PROVIDED == "user_provided"
        assert FieldSource.VERIFIED == "verified"

    def test_expiry_status_enum(self):
        assert ExpiryStatus.VALID == "valid"
        assert ExpiryStatus.EXPIRED == "expired"
        assert ExpiryStatus.UNKNOWN == "unknown"

    def test_extracted_field_creation(self):
        field = ExtractedField(field="name", value="Ravi Kumar", confidence=0.95, source=FieldSource.OCR)
        assert field.field == "name"
        assert field.value == "Ravi Kumar"
        assert field.confidence == 0.95
        assert field.source == FieldSource.OCR
        assert field.verified is False

    def test_extracted_field_with_verification(self):
        field = ExtractedField(
            field="name", value="Ravi Kumar", confidence=0.95,
            source=FieldSource.USER_PROVIDED, ocr_value="Ravi Kurnar", verified=True,
        )
        assert field.verified is True
        assert field.ocr_value == "Ravi Kurnar"

    def test_ocr_result_creation(self):
        result = OCRResult(
            extracted_text="Name: Ravi Kumar",
            pages=[OCRPageResult(page_number=1, text="Name: Ravi Kumar", confidence=0.9)],
            overall_confidence=0.9,
            language="en",
        )
        assert result.extracted_text == "Name: Ravi Kumar"
        assert len(result.pages) == 1
        assert result.overall_confidence == 0.9

    def test_document_validation_result(self):
        result = DocumentValidationResult(valid=True, errors=[], warnings=[])
        assert result.valid is True

    def test_document_validation_result_invalid(self):
        result = DocumentValidationResult(valid=False, errors=["Missing name"], missing_fields=["name"])
        assert result.valid is False
        assert "Missing name" in result.errors

    def test_required_documents_result(self):
        result = RequiredDocumentsResult(service_id="income_certificate", operation="new_application")
        assert result.service_id == "income_certificate"

    def test_document_match_result(self):
        result = DocumentMatchResult(required_type="identity_proof", matched=True, document_id="doc-1")
        assert result.matched is True

    def test_cross_document_check_consistent(self):
        result = CrossDocumentCheckResult(consistent=True, checked_fields=["name"])
        assert result.consistent is True

    def test_cross_document_check_inconsistent(self):
        result = CrossDocumentCheckResult(
            consistent=False,
            discrepancies=[{"field": "name", "values": ["Ravi Kumar", "Ravi K."]}],
        )
        assert result.consistent is False
        assert len(result.discrepancies) == 1
