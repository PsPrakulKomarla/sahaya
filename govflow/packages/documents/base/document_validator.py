from abc import ABC, abstractmethod
from typing import Any

from packages.documents.base.models import DocumentValidationResult, ExtractedField


class DocumentValidator(ABC):
    """Abstract base class for document validation.

    Validates extracted document fields against rules.
    """

    @abstractmethod
    async def validate(
        self,
        extracted_fields: list[ExtractedField],
        document_type: str,
        context: dict[str, Any] | None = None,
    ) -> DocumentValidationResult:
        """Validate extracted document fields.

        Args:
            extracted_fields: Fields extracted from the document.
            document_type: The type of document being validated.
            context: Optional validation context (e.g., service requirements).

        Returns:
            DocumentValidationResult with validity and any errors.
        """
