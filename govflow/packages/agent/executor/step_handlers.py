from packages.agent.executor.handlers import StepHandler
from packages.agent.models.tasks import WorkflowStep, ExecutionContext, StepType


class DiscoverServiceHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.DISCOVER_SERVICE.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "service_id": context.service_id,
            "jurisdiction": context.jurisdiction,
            "verified": True,
        }


class GetRequirementsHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.GET_REQUIREMENTS.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "requirements_fetched": True,
            "documents_needed": [],
        }


class CheckEligibilityHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.CHECK_ELIGIBILITY.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "eligible": True,
            "criteria_met": [],
        }


class ValidateDocumentsHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.VALIDATE_DOCUMENTS.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "documents_valid": True,
            "validated_count": 0,
        }


class PrepareApplicationHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.PREPARE_APPLICATION.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "prepared": True,
            "form_data": {},
        }


class BrowserExecutionHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.BROWSER_EXECUTION.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "browser_actions_completed": True,
            "pages_visited": 0,
        }


class ExtractDataHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.EXTRACT_DATA.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "data_extracted": True,
            "extracted_data": {},
        }


class HumanReviewHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.HUMAN_REVIEW.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "reviewed": True,
            "approved": True,
        }


class SubmitHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.SUBMIT.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "submitted": True,
            "reference_number": "MOCK-REF-001",
        }


class TrackApplicationHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.TRACK_APPLICATION.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "tracking_data": {},
            "status": "unknown",
        }


class RaiseGrievanceHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.RAISE_GRIEVANCE.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "grievance_submitted": True,
            "grievance_id": "MOCK-GRIEV-001",
        }


class UpdateRecordHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.UPDATE_RECORD.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "record_updated": True,
        }


class RenewHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.RENEW.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "renewed": True,
        }


class CompleteHandler(StepHandler):
    def can_handle(self, step_type: str) -> bool:
        return step_type == StepType.COMPLETE.value

    async def execute(self, step: WorkflowStep, context: ExecutionContext) -> dict:
        return {
            "task_completed": True,
        }
