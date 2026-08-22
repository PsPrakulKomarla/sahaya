from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from packages.documents.base.models import OCRResult, ExtractedField


class DocumentExtractor(ABC):
    """Abstract base class for document field extraction.

    Extracts structured fields from OCR text output.
    """

    @abstractmethod
    async def extract(
        self,
        ocr_result: OCRResult,
        document_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ExtractedField]:
        """Extract structured fields from OCR result.

        Args:
            ocr_result: The OCR output to extract from.
            document_type: The type of document being processed.
            context: Optional additional context for extraction.

        Returns:
            List of ExtractedField with values and confidence scores.
        """
        pass

    @abstractmethod
    def supported_document_types(self) -> List[str]:
        """Return list of document types this extractor can handle."""
        pass
