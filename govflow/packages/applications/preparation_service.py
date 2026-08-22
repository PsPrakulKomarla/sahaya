from typing import Any

from app.core.logging import get_logger

from packages.documents.base.models import (
    ExtractedField,
)
from packages.documents.matcher import DocumentMatcher
from packages.documents.requirement_engine import DocumentRequirementEngine
from packages.services.registry.registry import ServiceRegistry

logger = get_logger(__name__)

FORM_FIELD_MAPPING: dict[str, dict[str, str]] = {
    "income_certificate": {
        "applicant_name": "name",
        "date_of_birth": "date_of_birth",
        "address": "address",
        "annual_income": "net_pay",
    },
    "birth_certificate": {
        "child_name": "child_name",
        "date_of_birth": "date_of_birth",
        "place_of_birth": "place_of_birth",
        "father_name": "father_name",
        "mother_name": "mother_name",
    },
}


class ApplicationPreparationService:
    """Prepares application drafts from user data, documents, and service requirements."""

    def __init__(
        self,
        requirement_engine: DocumentRequirementEngine | None = None,
        document_matcher: DocumentMatcher | None = None,
        registry: ServiceRegistry | None = None,
    ):
        self._requirement_engine = requirement_engine or DocumentRequirementEngine()
        self._document_matcher = document_matcher or DocumentMatcher()
        self._registry = registry

    async def prepare_application(
        self,
        service_id: str,
        user_id: str,
        user_data: dict[str, Any],
        user_documents: list[dict[str, Any]],
        document_extracted_fields: dict[str, list[ExtractedField]],
        jurisdiction: str | None = None,
    ) -> dict[str, Any]:
        """Prepare an application draft."""
        requirements = await self._requirement_engine.get_requirements(
            service_id, "new_application", jurisdiction
        )

        availability = self._document_matcher.check_availability(
            [
                {"document_type": r.document_type, "display_name": r.display_name, "mandatory": r.mandatory}
                for r in requirements.requirements
            ],
            user_documents,
        )

        missing_mandatory = [
            a for a in availability if a.mandatory and not a.available
        ]

        if missing_mandatory:
            return {
                "status": "requirements_pending",
                "missing_documents": [
                    {"type": a.required_type, "display_name": a.display_name}
                    for a in missing_mandatory
                ],
                "available_documents": [
                    {"type": a.required_type, "display_name": a.display_name}
                    for a in availability
                    if a.available
                ],
            }

        form_data = self._build_form_data(service_id, user_data, document_extracted_fields)

        all_fields: list[ExtractedField] = []
        for fields in document_extracted_fields.values():
            all_fields.extend(fields)

        cross_doc_check = self._document_matcher.check_cross_document_consistency(
            [fields for fields in document_extracted_fields.values()]
        )

        if not cross_doc_check.consistent:
            return {
                "status": "needs_review",
                "form_data": form_data,
                "cross_document_issues": cross_doc_check.discrepancies,
                "document_ids": [str(doc.get("id", "")) for doc in user_documents],
            }

        missing_fields = self._find_missing_fields(form_data, service_id)
        if missing_fields:
            return {
                "status": "missing_information",
                "form_data": form_data,
                "missing_fields": missing_fields,
                "document_ids": [str(doc.get("id", "")) for doc in user_documents],
            }

        return {
            "status": "ready_for_review",
            "form_data": form_data,
            "document_ids": [str(doc.get("id", "")) for doc in user_documents],
            "requirements_met": True,
            "cross_document_check": {
                "consistent": cross_doc_check.consistent,
                "checked_fields": cross_doc_check.checked_fields,
            },
        }

    def _build_form_data(
        self,
        service_id: str,
        user_data: dict[str, Any],
        document_extracted_fields: dict[str, list[ExtractedField]],
    ) -> dict[str, Any]:
        """Build form data by mapping document fields to application fields."""
        mapping = FORM_FIELD_MAPPING.get(service_id, {})
        form_data: dict[str, Any] = {}

        all_extracted: dict[str, Any] = {}
        for fields in document_extracted_fields.values():
            for field in fields:
                if field.value and (field.verified or field.confidence > 0.7) and field.field not in all_extracted:
                    all_extracted[field.field] = field.value

        for app_field, source_field in mapping.items():
            if source_field in all_extracted:
                form_data[app_field] = all_extracted[source_field]
            elif app_field in user_data:
                form_data[app_field] = user_data[app_field]

        for key, value in user_data.items():
            if key not in form_data:
                form_data[key] = value

        return form_data

    def _find_missing_fields(
        self, form_data: dict[str, Any], service_id: str
    ) -> list[str]:
        """Find required fields that are missing from form data."""
        required_fields = {
            "income_certificate": ["applicant_name", "address", "annual_income"],
            "birth_certificate": ["child_name", "date_of_birth"],
        }

        required = required_fields.get(service_id, [])
        return [f for f in required if not form_data.get(f)]
