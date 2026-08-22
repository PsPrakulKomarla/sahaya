import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.documents.base.models import ExtractedField, FieldSource, OCRResult
from packages.documents.extraction.extractor import DefaultDocumentExtractor
from packages.documents.validation.validator import DefaultDocumentValidator


class TestDocumentExtractor:
    @pytest.mark.asyncio
    async def test_extract_identity_fields(self):
        extractor = DefaultDocumentExtractor()
        ocr_result = OCRResult(
            extracted_text="Name: Ravi Kumar\nDate of Birth: 12/04/2000\nGender: Male\nAddress: 123 Main Street, Bengaluru",
            overall_confidence=0.92,
        )
        fields = await extractor.extract(ocr_result, "identity_proof")
        field_names = [f.field for f in fields]
        assert "name" in field_names
        assert "date_of_birth" in field_names

    @pytest.mark.asyncio
    async def test_extract_address_fields(self):
        extractor = DefaultDocumentExtractor()
        ocr_result = OCRResult(
            extracted_text="Name: Ravi Kumar\nAddress: 123 Main Street, Bengaluru",
            overall_confidence=0.88,
        )
        fields = await extractor.extract(ocr_result, "address_proof")
        field_names = [f.field for f in fields]
        assert "name" in field_names
        assert "address" in field_names

    @pytest.mark.asyncio
    async def test_extract_birth_certificate_fields(self):
        extractor = DefaultDocumentExtractor()
        ocr_result = OCRResult(
            extracted_text="Child Name: Ravi Kumar\nDate of Birth: 12/04/2000\nFather Name: Suresh Kumar",
            overall_confidence=0.94,
        )
        fields = await extractor.extract(ocr_result, "birth_certificate")
        field_names = [f.field for f in fields]
        assert "child_name" in field_names
        assert "date_of_birth" in field_names
        assert "father_name" in field_names

    @pytest.mark.asyncio
    async def test_extract_passport_fields(self):
        extractor = DefaultDocumentExtractor()
        ocr_result = OCRResult(
            extracted_text="Given Name: RAVI\nSurname: KUMAR\nDate of Birth: 12/04/2000",
            overall_confidence=0.95,
        )
        fields = await extractor.extract(ocr_result, "passport")
        field_names = [f.field for f in fields]
        assert "given_name" in field_names
        assert "surname" in field_names

    @pytest.mark.asyncio
    async def test_extract_generic_document(self):
        extractor = DefaultDocumentExtractor()
        ocr_result = OCRResult(
            extracted_text="Name: Ravi Kumar\nDate: 01/01/2026",
            overall_confidence=0.75,
        )
        fields = await extractor.extract(ocr_result, "unknown_type")
        assert isinstance(fields, list)

    def test_supported_document_types(self):
        extractor = DefaultDocumentExtractor()
        types = extractor.supported_document_types()
        assert "identity_proof" in types
        assert "address_proof" in types
        assert "income_proof" in types
        assert "birth_certificate" in types
        assert "passport" in types


class TestDocumentValidator:
    @pytest.mark.asyncio
    async def test_validate_identity_valid(self):
        validator = DefaultDocumentValidator()
        fields = [
            ExtractedField(field="name", value="Ravi Kumar", confidence=0.95),
            ExtractedField(field="date_of_birth", value="2000-04-12", confidence=0.9),
        ]
        result = await validator.validate(fields, "identity_proof")
        assert result.valid is True

    @pytest.mark.asyncio
    async def test_validate_identity_missing_name(self):
        validator = DefaultDocumentValidator()
        fields = [
            ExtractedField(field="date_of_birth", value="2000-04-12", confidence=0.9),
        ]
        result = await validator.validate(fields, "identity_proof")
        assert result.valid is False
        assert "name" in result.missing_fields

    @pytest.mark.asyncio
    async def test_validate_with_low_confidence_warning(self):
        validator = DefaultDocumentValidator()
        fields = [
            ExtractedField(field="name", value="Ravi Kumar", confidence=0.5, source=FieldSource.OCR),
            ExtractedField(field="date_of_birth", value="2000-04-12", confidence=0.9),
        ]
        result = await validator.validate(fields, "identity_proof")
        assert any("low OCR confidence" in w for w in result.warnings)

    @pytest.mark.asyncio
    async def test_validate_address_proof(self):
        validator = DefaultDocumentValidator()
        fields = [
            ExtractedField(field="name", value="Ravi Kumar", confidence=0.9),
            ExtractedField(field="address", value="123 Main Street, Bengaluru", confidence=0.9),
        ]
        result = await validator.validate(fields, "address_proof")
        assert result.valid is True

    @pytest.mark.asyncio
    async def test_validate_birth_certificate(self):
        validator = DefaultDocumentValidator()
        fields = [
            ExtractedField(field="child_name", value="Ravi Kumar", confidence=0.9),
            ExtractedField(field="date_of_birth", value="2000-04-12", confidence=0.9),
        ]
        result = await validator.validate(fields, "birth_certificate")
        assert result.valid is True
