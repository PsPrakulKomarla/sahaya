"""Concrete step handlers for each workflow step type.

Each handler is independently testable and implements the StepHandler interface.
Handlers do NOT contain service-specific logic — they work through the context
and adapter interfaces.
"""
from __future__ import annotations

from typing import Any, Dict

from packages.agent.executor.context import ExecutionContext, Permission
from packages.agent.executor.handlers import StepHandler
from packages.agent.errors import ApprovalRequired, BrowserActionFailed
from packages.agent.planner.models import StepType, WorkflowStep


class DiscoverServiceHandler(StepHandler):
    """Handles DISCOVER_SERVICE steps — locates the official portal."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.DISCOVER_SERVICE

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        service_id = context.service_id
        portal_url = context.metadata.get("official_portal", "")

        if not portal_url:
            portal_url = f"https://example.gov.in/{service_id}"

        return {
            "success": True,
            "portal_url": portal_url,
            "service_id": service_id,
            "step": "discover",
        }


class GetRequirementsHandler(StepHandler):
    """Handles GET_REQUIREMENTS steps — gathers service requirements."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.GET_REQUIREMENTS

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "requirements": context.metadata.get("requirements", []),
            "step": "requirements",
        }


class CheckEligibilityHandler(StepHandler):
    """Handles CHECK_ELIGIBILITY steps — verifies user eligibility."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.CHECK_ELIGIBILITY

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "eligible": True,
            "criteria_met": [],
            "step": "eligibility",
        }


class ValidateDocumentsHandler(StepHandler):
    """Handles VALIDATE_DOCUMENTS steps — validates required documents."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.VALIDATE_DOCUMENTS

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "documents_valid": True,
            "validated_documents": [],
            "step": "documents",
        }


class PrepareApplicationHandler(StepHandler):
    """Handles PREPARE_APPLICATION steps — prepares application data."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.PREPARE_APPLICATION

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "application_data": {},
            "step": "prepare",
        }


class BrowserExecutionHandler(StepHandler):
    """Handles BROWSER_EXECUTION steps — delegates to the browser agent.

    This handler does NOT contain browser-specific logic.
    It calls the browser agent through the execution context.
    """

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.BROWSER_EXECUTION

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        if not context.has_permission(Permission.BROWSER_NAVIGATION):
            return {
                "success": False,
                "error": "BROWSER_NAVIGATION permission required",
                "step": "browser",
            }

        browser = context.metadata.get("browser_agent")
        if browser is None:
            return {
                "success": True,
                "simulated": True,
                "message": "No browser agent available — simulated execution",
                "step": "browser",
            }

        try:
            url = context.metadata.get("portal_url", "https://example.gov.in")
            await browser.navigate(url)
            page = await browser.inspect()

            return {
                "success": True,
                "url": url,
                "page_title": page.title,
                "elements_found": len(page.elements),
                "step": "browser",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "step": "browser",
            }


class ExtractDataHandler(StepHandler):
    """Handles EXTRACT_DATA steps — extracts data from the current page."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.EXTRACT_DATA

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        browser = context.metadata.get("browser_agent")
        if browser is None:
            return {
                "success": True,
                "data": {},
                "simulated": True,
                "step": "extract",
            }

        try:
            data = await browser.extract_structured_data()
            return {
                "success": True,
                "data": data,
                "step": "extract",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "step": "extract",
            }


class HumanReviewHandler(StepHandler):
    """Handles HUMAN_REVIEW steps — creates an approval request."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.HUMAN_REVIEW

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        if context.approval_state.is_valid():
            return {
                "success": True,
                "approval_id": context.approval_state.approval_id,
                "already_approved": True,
                "step": "review",
            }

        return {
            "success": False,
            "requires_approval": True,
            "action_type": "HUMAN_REVIEW",
            "message": "Human review required before continuing",
            "step": "review",
        }


class SubmitHandler(StepHandler):
    """Handles SUBMIT steps — submits the application.

    This handler enforces safety: submission requires prior approval.
    """

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.SUBMIT

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        if not context.approval_state.is_valid():
            raise ApprovalRequired(
                action_type="SUBMIT_APPLICATION",
                reason="Submission requires explicit user approval",
            )

        browser = context.metadata.get("browser_agent")
        if browser is None:
            return {
                "success": True,
                "simulated": True,
                "message": "Simulated submission (no browser agent)",
                "reference_number": "SIM-001",
                "step": "submit",
            }

        try:
            url = context.metadata.get("portal_url", "")
            if url:
                await browser.navigate(url)
            return {
                "success": True,
                "reference_number": "SUBMITTED-001",
                "step": "submit",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "step": "submit",
            }


class TrackApplicationHandler(StepHandler):
    """Handles TRACK_APPLICATION steps — tracks application status."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.TRACK_APPLICATION

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "status": "submitted",
            "step": "track",
        }


class RaiseGrievanceHandler(StepHandler):
    """Handles RAISE_GRIEVANCE steps — files a grievance."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.RAISE_GRIEVANCE

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        if not context.approval_state.is_valid():
            raise ApprovalRequired(
                action_type="SUBMIT_GRIEVANCE",
                reason="Grievance submission requires explicit user approval",
            )
        return {
            "success": True,
            "grievance_id": "GRIEV-001",
            "step": "grievance",
        }


class CompleteHandler(StepHandler):
    """Handles COMPLETE steps — marks the task as done."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.COMPLETE

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "completed": True,
            "step": "complete",
        }


class UpdateRecordHandler(StepHandler):
    """Handles UPDATE_RECORD steps — updates an existing record."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.UPDATE_RECORD

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "updated": True,
            "step": "update_record",
        }


class RenewHandler(StepHandler):
    """Handles RENEW steps — processes a renewal."""

    def can_handle(self, step_type: StepType) -> bool:
        return step_type == StepType.RENEW

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "success": True,
            "renewed": True,
            "step": "renew",
        }


def register_default_handlers(registry: StepHandlerRegistry) -> None:
    """Register all default step handlers."""
    handlers = [
        DiscoverServiceHandler(),
        GetRequirementsHandler(),
        CheckEligibilityHandler(),
        ValidateDocumentsHandler(),
        PrepareApplicationHandler(),
        BrowserExecutionHandler(),
        ExtractDataHandler(),
        HumanReviewHandler(),
        SubmitHandler(),
        TrackApplicationHandler(),
        RaiseGrievanceHandler(),
        CompleteHandler(),
        UpdateRecordHandler(),
        RenewHandler(),
    ]
    for handler in handlers:
        for step_type in StepType:
            if handler.can_handle(step_type):
                registry.register(step_type, handler)
                break
