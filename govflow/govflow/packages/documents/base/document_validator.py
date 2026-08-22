from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from packages.documents.base.models import ExtractedField, DocumentValidationResult


class DocumentValidator(ABC):
    """Abstract base class for document validation.

    Validates extracted document fields against rules.
    """

    @abstractmethod
    async def validate(
        self,
        extracted_fields: List[ExtractedField],
        document_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DocumentValidationResult:
        """Validate extracted document fields.

        Args:
            extracted_fields: Fields extracted from the document.
            document_type: The type of document being validated.
            context: Optional validation context (e.g., service requirements).

        Returns:
            DocumentValidationResult with validity and any errors.
        """
        pass
