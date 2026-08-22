from abc import ABC, abstractmethod
from typing import Optional, List
from packages.documents.base.models import OCRResult


class OCRProvider(ABC):
    """Abstract base class for OCR providers.

    Each provider implements document text extraction.
    Providers are swappable without modifying DocumentService.
    """

    @abstractmethod
    async def process(self, file_path: str, language: Optional[str] = None) -> OCRResult:
        """Process a document file and extract text.

        Args:
            file_path: Path to the document file.
            language: Optional language hint (e.g., 'en', 'kn', 'hi').

        Returns:
            OCRResult with extracted text, confidence, and metadata.
        """
        pass

    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        pass

    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this OCR provider."""
        pass

    def supports_language(self, language: str) -> bool:
        """Check if a specific language is supported."""
        return language in self.supported_languages()
