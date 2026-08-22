from typing import Any, ClassVar

from app.core.logging import get_logger

from packages.documents.base.document_validator import DocumentValidator
from packages.documents.base.models import (
    DocumentValidationResult,
    ExtractedField,
    FieldSource,
)

logger = get_logger(__name__)


class DefaultDocumentValidator(DocumentValidator):
    """Default document validator with basic field validation rules.

    Validates extracted fields based on document type requirements.
    """

    REQUIRED_FIELDS: ClassVar[dict[str, list[str]]] = {
        "identity_proof": ["name", "date_of_birth"],
        "address_proof": ["name", "address"],
        "income_proof": ["employee_name"],
        "birth_certificate": ["child_name", "date_of_birth"],
        "passport": ["given_name", "surname", "date_of_birth"],
    }

    FIELD_FORMATS: ClassVar[dict[str, dict[str, Any]]] = {
        "date_of_birth": {"pattern": r"^\d{4}-\d{2}-\d{2}$", "description": "YYYY-MM-DD format"},
        "date_of_issue": {"pattern": r"^\d{4}-\d{2}-\d{2}$", "description": "YYYY-MM-DD format"},
        "date_of_expiry": {"pattern": r"^\d{4}-\d{2}-\d{2}$", "description": "YYYY-MM-DD format"},
        "aadhaar_number": {"pattern": r"^\d{4}\s?\d{4}\s?\d{4}$", "description": "12-digit Aadhaar number"},
    }

    async def validate(
        self,
        extracted_fields: list[ExtractedField],
        document_type: str,
        context: dict[str, Any] | None = None,
    ) -> DocumentValidationResult:
        """Validate extracted fields against document type rules."""
        errors: list[str] = []
        warnings: list[str] = []
        missing_fields: list[str] = []
        field_formats: dict[str, bool] = {}

        fields_by_name = {f.field: f for f in extracted_fields}

        required = self.REQUIRED_FIELDS.get(document_type, [])
        for field_name in required:
            field = fields_by_name.get(field_name)
            if not field or not field.value:
                missing_fields.append(field_name)
                errors.append(f"Required field '{field_name}' is missing or empty")

        for field in extracted_fields:
            if field.field in self.FIELD_FORMATS:
                format_rule = self.FIELD_FORMATS[field.field]
                import re

                if field.value and not re.match(format_rule["pattern"], str(field.value)):
                    field_formats[field.field] = False
                    errors.append(
                        f"Field '{field.field}' has invalid format. Expected: {format_rule['description']}"
                    )
                else:
                    field_formats[field.field] = True

        for field in extracted_fields:
            if field.source == FieldSource.OCR and field.confidence < 0.7:
                warnings.append(
                    f"Field '{field.field}' has low OCR confidence ({field.confidence:.2f})"
                )

        if document_type == "identity_proof":
            name_field = fields_by_name.get("name")
            if name_field and name_field.value and len(str(name_field.value).strip()) < 2:
                errors.append("Name field appears to be too short")

        if document_type == "address_proof":
            address_field = fields_by_name.get("address")
            if address_field and address_field.value and len(str(address_field.value).strip()) < 5:
                warnings.append("Address field appears to be very short")

        valid = len(errors) == 0

        if not valid:
            logger.info(
                "document_validation_failed",
                document_type=document_type,
                error_count=len(errors),
                missing_count=len(missing_fields),
            )

        return DocumentValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            missing_fields=missing_fields,
            field_formats=field_formats,
        )
