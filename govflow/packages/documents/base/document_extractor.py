from abc import ABC, abstractmethod
from typing import Any

from packages.documents.base.models import ExtractedField, OCRResult


class DocumentExtractor(ABC):
    """Abstract base class for document field extraction.

    Extracts structured fields from OCR text output.
    """

    @abstractmethod
    async def extract(
        self,
        ocr_result: OCRResult,
        document_type: str,
        context: dict[str, Any] | None = None,
    ) -> list[ExtractedField]:
        """Extract structured fields from OCR result.

        Args:
            ocr_result: The OCR output to extract from.
            document_type: The type of document being processed.
            context: Optional additional context for extraction.

        Returns:
            List of ExtractedField with values and confidence scores.
        """

    @abstractmethod
    def supported_document_types(self) -> list[str]:
        """Return list of document types this extractor can handle."""
