from packages.documents.base.models import OCRPageResult, OCRResult
from packages.documents.base.ocr_provider import OCRProvider


class MockOCRProvider(OCRProvider):
    """Mock OCR provider for testing and development.

    Simulates OCR processing without requiring actual OCR dependencies.
    Returns predefined or pattern-matched text based on file name hints.
    """

    def __init__(self):
        self._mock_results: dict[str, OCRResult] = {}

    def provider_name(self) -> str:
        return "mock_ocr"

    def supported_languages(self) -> list[str]:
        return ["en", "kn", "hi"]

    def set_mock_result(self, file_name: str, result: OCRResult) -> None:
        """Set a mock OCR result for a specific file name."""
        self._mock_results[file_name] = result

    async def process(self, file_path: str, language: str | None = None) -> OCRResult:
        """Process a document using mock OCR.

        Returns simulated OCR output based on file name patterns.
        """
        file_name = file_path.split("/")[-1].split("\\")[-1].lower()

        if file_name in self._mock_results:
            return self._mock_results[file_name]

        if "aadhaar" in file_name or "identity" in file_name:
            return self._mock_identity_document(file_name, language)
        elif "address" in file_name or "electricity" in file_name:
            return self._mock_address_proof(file_name, language)
        elif "income" in file_name or "salary" in file_name or "form16" in file_name:
            return self._mock_income_proof(file_name, language)
        elif "birth" in file_name:
            return self._mock_birth_certificate(file_name, language)
        elif "passport" in file_name:
            return self._mock_passport(file_name, language)
        else:
            return self._mock_generic_document(file_name, language)

    def _mock_identity_document(self, file_name: str, language: str | None = None) -> OCRResult:
        text = (
            "Name: Ravi Kumar\n"
            "Date of Birth: 12/04/2000\n"
            "Gender: Male\n"
            "Address: 123 Main Street, Bengaluru, Karnataka 560001\n"
            "Aadhaar Number: 1234 5678 9012\n"
        )
        return OCRResult(
            extracted_text=text,
            pages=[
                OCRPageResult(
                    page_number=1,
                    text=text,
                    confidence=0.92,
                    language=language or "en",
                )
            ],
            overall_confidence=0.92,
            language=language or "en",
            metadata={"document_category": "identity"},
        )

    def _mock_address_proof(self, file_name: str, language: str | None = None) -> OCRResult:
        text = (
            "ELECTRICITY BILL\n"
            "Consumer Number: 1234567890\n"
            "Name: Ravi Kumar\n"
            "Address: 123 Main Street, Bengaluru, Karnataka 560001\n"
            "Bill Date: 01/08/2026\n"
            "Amount Due: Rs. 1,250.00\n"
        )
        return OCRResult(
            extracted_text=text,
            pages=[
                OCRPageResult(
                    page_number=1,
                    text=text,
                    confidence=0.88,
                    language=language or "en",
                )
            ],
            overall_confidence=0.88,
            language=language or "en",
            metadata={"document_category": "address"},
        )

    def _mock_income_proof(self, file_name: str, language: str | None = None) -> OCRResult:
        text = (
            "SALARY SLIP\n"
            "Employee Name: Ravi Kumar\n"
            "Employee ID: EMP-12345\n"
            "Month: August 2026\n"
            "Basic Salary: Rs. 50,000.00\n"
            "Total Deductions: Rs. 8,000.00\n"
            "Net Pay: Rs. 42,000.00\n"
        )
        return OCRResult(
            extracted_text=text,
            pages=[
                OCRPageResult(
                    page_number=1,
                    text=text,
                    confidence=0.90,
                    language=language or "en",
                )
            ],
            overall_confidence=0.90,
            language=language or "en",
            metadata={"document_category": "income"},
        )

    def _mock_birth_certificate(self, file_name: str, language: str | None = None) -> OCRResult:
        text = (
            "BIRTH CERTIFICATE\n"
            "Child Name: Ravi Kumar\n"
            "Date of Birth: 12/04/2000\n"
            "Place of Birth: Bengaluru\n"
            "Father Name: Suresh Kumar\n"
            "Mother Name: Priya Kumar\n"
        )
        return OCRResult(
            extracted_text=text,
            pages=[
                OCRPageResult(
                    page_number=1,
                    text=text,
                    confidence=0.94,
                    language=language or "en",
                )
            ],
            overall_confidence=0.94,
            language=language or "en",
            metadata={"document_category": "birth"},
        )

    def _mock_passport(self, file_name: str, language: str | None = None) -> OCRResult:
        text = (
            "REPUBLIC OF INDIA\n"
            "PASSPORT\n"
            "Surname: KUMAR\n"
            "Given Name: RAVI\n"
            "Date of Birth: 12/04/2000\n"
            "Place of Birth: BENGALURU\n"
            "Date of Issue: 01/01/2020\n"
            "Date of Expiry: 31/12/2029\n"
        )
        return OCRResult(
            extracted_text=text,
            pages=[
                OCRPageResult(
                    page_number=1,
                    text=text,
                    confidence=0.95,
                    language=language or "en",
                )
            ],
            overall_confidence=0.95,
            language=language or "en",
            metadata={"document_category": "passport"},
        )

    def _mock_generic_document(self, file_name: str, language: str | None = None) -> OCRResult:
        text = f"Document: {file_name}\nContent: Generic document text\n"
        return OCRResult(
            extracted_text=text,
            pages=[
                OCRPageResult(
                    page_number=1,
                    text=text,
                    confidence=0.75,
                    language=language or "en",
                )
            ],
            overall_confidence=0.75,
            language=language or "en",
            metadata={"document_category": "generic"},
        )
