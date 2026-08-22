import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger

from packages.services.registry.registry import ServiceRegistry

logger = get_logger(__name__)

STATUS_NORMALIZATION: dict[str, str] = {
    "submitted": "submitted",
    "under_review": "processing",
    "processing": "processing",
    "scrutiny": "processing",
    "under scrutiny": "processing",
    "verification": "processing",
    "returned": "action_required",
    "returned for correction": "action_required",
    "correction required": "action_required",
    "action required": "action_required",
    "issued": "completed",
    "approved": "completed",
    "delivered": "completed",
    "rejected": "failed",
    "failed": "failed",
    "cancelled": "cancelled",
}


class ApplicationService:
    """Manages application lifecycle: create, update, validate, review, submit."""

    def __init__(self, registry: ServiceRegistry | None = None):
        self._registry = registry

    def _get_registry(self) -> ServiceRegistry:
        if self._registry is None:
            from packages.services import get_registry
            self._registry = get_registry()
        return self._registry

    def create_draft(
        self,
        user_id: str,
        service_id: str,
        form_data: dict[str, Any] | None = None,
        document_ids: list[str] | None = None,
        jurisdiction: str | None = None,
    ) -> dict[str, Any]:
        application_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        logger.info("application_created", application_id=application_id, user_id=user_id, service_id=service_id)
        return {
            "id": application_id,
            "user_id": user_id,
            "service_id": service_id,
            "jurisdiction_id": jurisdiction,
            "status": "draft",
            "form_data": form_data or {},
            "document_ids": document_ids or [],
            "created_at": now,
            "updated_at": now,
        }

    def update_draft(
        self,
        application: dict[str, Any],
        form_data: dict[str, Any] | None = None,
        document_ids: list[str] | None = None,
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        has_changes = self._has_material_changes(application, form_data, document_ids)

        if form_data is not None:
            application["form_data"] = form_data
        if document_ids is not None:
            application["document_ids"] = document_ids
        application["updated_at"] = datetime.now(timezone.utc).isoformat()

        if approval_id and has_changes:
            application["approval_id"] = None
            application["approval_invalidated"] = True
            logger.info("approval_invalidated", application_id=application.get("id"), reason="material_changes")

        return application

    def _has_material_changes(
        self,
        application: dict[str, Any],
        new_form_data: dict[str, Any] | None,
        new_document_ids: list[str] | None,
    ) -> bool:
        if new_form_data is not None:
            old_data = application.get("form_data", {})
            material_keys = {"applicant_name", "address", "service_id", "income"}
            for key in material_keys:
                if old_data.get(key) != new_form_data.get(key):
                    return True
        if new_document_ids is not None:
            old_docs = {str(d) for d in application.get("document_ids", [])}
            new_docs = {str(d) for d in new_document_ids}
            if old_docs != new_docs:
                return True
        return False

    def validate_draft(self, application: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        missing_fields: list[str] = []
        form_data = application.get("form_data", {})
        document_ids = application.get("document_ids", [])

        if not form_data:
            errors.append("Form data is empty")
        if not document_ids:
            warnings.append("No documents attached")

        required_fields = self._get_required_fields(application.get("service_id", ""))
        for field in required_fields:
            if not form_data.get(field):
                missing_fields.append(field)
                errors.append(f"Required field '{field}' is missing")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "missing_fields": missing_fields}

    def _get_required_fields(self, service_id: str) -> list[str]:
        required = {
            "income_certificate": ["applicant_name", "address"],
            "birth_certificate": ["child_name", "date_of_birth"],
        }
        return required.get(service_id, [])

    def mark_ready_for_review(self, application: dict[str, Any]) -> dict[str, Any]:
        validation = self.validate_draft(application)
        if not validation["valid"]:
            return {"success": False, "application": application, "validation": validation}
        application["status"] = "ready_for_review"
        application["updated_at"] = datetime.now(timezone.utc).isoformat()
        return {"success": True, "application": application}

    def mark_awaiting_approval(self, application: dict[str, Any]) -> dict[str, Any]:
        application["status"] = "awaiting_approval"
        application["updated_at"] = datetime.now(timezone.utc).isoformat()
        return application

    async def submit(self, application: dict[str, Any], approval_id: str | None = None) -> dict[str, Any]:
        if application.get("status") != "awaiting_approval":
            return {"success": False, "error": "Application must be in awaiting_approval status before submission"}
        if application.get("approval_invalidated"):
            return {"success": False, "error": "Approval has been invalidated due to material changes. Please review again."}

        revalidation = self.validate_draft(application)
        if not revalidation["valid"]:
            return {"success": False, "error": "Application failed pre-submission validation", "validation": revalidation}

        registry = self._get_registry()
        adapter = registry.get_service(application.get("service_id", ""))
        if not adapter:
            return {"success": False, "error": "Service adapter not found"}

        submission_data = {
            "full_name": application.get("form_data", {}).get("applicant_name", ""),
            "father_name": application.get("form_data", {}).get("father_name", ""),
            "address": application.get("form_data", {}).get("address", ""),
            "income": application.get("form_data", {}).get("annual_income", 0),
        }

        try:
            result = await adapter.create_application(submission_data)
            if result.success:
                application["status"] = "submitted"
                application["submitted_at"] = datetime.now(timezone.utc).isoformat()
                application["reference_number"] = result.data.get("reference_number")
                application["updated_at"] = datetime.now(timezone.utc).isoformat()
                logger.info("application_submitted", application_id=application.get("id"), reference_number=application.get("reference_number"))
                return {"success": True, "application": application, "submission_result": result.data}
            else:
                application["status"] = "failed"
                return {"success": False, "error": result.error.message if result.error else "Submission failed", "application": application}
        except (RuntimeError, ValueError, KeyError, TypeError) as e:  # Broad catch for external service
            logger.error("submission_error", application_id=application.get("id"), error=str(e))
            application["status"] = "failed"
            return {"success": False, "error": str(e), "application": application}

    def create_timeline_event(
        self,
        application_id: str,
        event_type: str,
        status: str | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "application_id": application_id,
            "event_type": event_type,
            "status": status,
            "note": note,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_timeline(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(events, key=lambda e: e.get("timestamp", ""))
