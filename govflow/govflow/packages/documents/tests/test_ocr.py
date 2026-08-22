import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.documents.base.ocr_provider import OCRProvider
from packages.documents.base.models import OCRResult
from packages.documents.ocr.mock_provider import MockOCRProvider


class TestMockOCRProvider:
    def test_implements_interface(self):
        provider = MockOCRProvider()
        assert isinstance(provider, OCRProvider)
        assert provider.provider_name() == "mock_ocr"
        assert "en" in provider.supported_languages()
        assert "kn" in provider.supported_languages()
        assert "hi" in provider.supported_languages()

    def test_supports_language(self):
        provider = MockOCRProvider()
        assert provider.supports_language("en") is True
        assert provider.supports_language("xyz") is False

    @pytest.mark.asyncio
    async def test_process_identity(self):
        provider = MockOCRProvider()
        result = await provider.process("aadhaar_card.pdf")
        assert result.extracted_text
        assert result.overall_confidence > 0
        assert len(result.pages) > 0

    @pytest.mark.asyncio
    async def test_process_address(self):
        provider = MockOCRProvider()
        result = await provider.process("electricity_bill.pdf")
        assert "Ravi Kumar" in result.extracted_text

    @pytest.mark.asyncio
    async def test_process_income(self):
        provider = MockOCRProvider()
        result = await provider.process("salary_slip.pdf")
        assert "Ravi Kumar" in result.extracted_text

    @pytest.mark.asyncio
    async def test_process_birth(self):
        provider = MockOCRProvider()
        result = await provider.process("birth_certificate.pdf")
        assert "BIRTH CERTIFICATE" in result.extracted_text

    @pytest.mark.asyncio
    async def test_process_passport(self):
        provider = MockOCRProvider()
        result = await provider.process("passport.pdf")
        assert "PASSPORT" in result.extracted_text

    @pytest.mark.asyncio
    async def test_process_generic(self):
        provider = MockOCRProvider()
        result = await provider.process("random_document.pdf")
        assert result.extracted_text

    def test_set_custom_result(self):
        provider = MockOCRProvider()
        custom = OCRResult(extracted_text="Custom text", overall_confidence=0.5)
        provider.set_mock_result("custom.pdf", custom)
        assert "custom.pdf" in provider._mock_results

    @pytest.mark.asyncio
    async def test_custom_result_returned(self):
        provider = MockOCRProvider()
        custom = OCRResult(extracted_text="Custom OCR", overall_confidence=0.99)
        provider.set_mock_result("custom.pdf", custom)
        result = await provider.process("custom.pdf")
        assert result.extracted_text == "Custom OCR"
        assert result.overall_confidence == 0.99
