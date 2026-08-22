from typing import Optional, List
from packages.agent.models.tasks import (
    TaskType,
    WorkflowPlan,
    WorkflowStep,
    StepType,
    RetryPolicy,
)
from packages.services.intent.models import Intent, IntentType
from packages.services.registry.models import ServiceResolution, ResolutionStatus
from packages.services.base.models import ServiceCapability


STEP_TYPE_MAP = {
    IntentType.SERVICE_DISCOVERY: StepType.DISCOVER_SERVICE,
    IntentType.ELIGIBILITY_CHECK: StepType.CHECK_ELIGIBILITY,
    IntentType.DOCUMENT_REQUIREMENTS: StepType.GET_REQUIREMENTS,
    IntentType.NEW_APPLICATION: StepType.BROWSER_EXECUTION,
    IntentType.UPDATE_RECORD: StepType.UPDATE_RECORD,
    IntentType.RENEWAL: StepType.RENEW,
    IntentType.TRACK_APPLICATION: StepType.TRACK_APPLICATION,
    IntentType.RAISE_GRIEVANCE: StepType.RAISE_GRIEVANCE,
    IntentType.GENERAL_SERVICE_INFORMATION: StepType.DISCOVER_SERVICE,
}

CAPABILITY_STEP_MAP = {
    ServiceCapability.DISCOVER: StepType.DISCOVER_SERVICE,
    ServiceCapability.ELIGIBILITY_CHECK: StepType.CHECK_ELIGIBILITY,
    ServiceCapability.DOCUMENT_REQUIREMENTS: StepType.GET_REQUIREMENTS,
    ServiceCapability.NEW_APPLICATION: StepType.BROWSER_EXECUTION,
    ServiceCapability.UPDATE_RECORD: StepType.UPDATE_RECORD,
    ServiceCapability.RENEW: StepType.RENEW,
    ServiceCapability.TRACK_APPLICATION: StepType.TRACK_APPLICATION,
    ServiceCapability.RAISE_GRIEVANCE: StepType.RAISE_GRIEVANCE,
}

SENSITIVE_STEPS = {StepType.SUBMIT, StepType.UPDATE_RECORD, StepType.RENEW}


class TaskPlanner:
    """Converts intent + resolution into a WorkflowPlan."""

    def create_plan(
        self,
        intent: Intent,
        resolution: ServiceResolution,
    ) -> WorkflowPlan:
        if resolution.status != ResolutionStatus.RESOLVED:
            return WorkflowPlan(
                task_type=TaskType.OTHER,
                service_id=resolution.service_id or "",
                steps=[],
            )

        task_type = self._determine_task_type(intent)
        capabilities = self._parse_capabilities(resolution.capabilities)
        steps = self._build_steps(task_type, capabilities, intent)

        return WorkflowPlan(
            task_type=task_type,
            service_id=resolution.service_id or "",
            steps=steps,
            metadata={
                "service_name": resolution.service_name,
                "jurisdiction": resolution.jurisdiction.state if resolution.jurisdiction else None,
                "workflow_version": resolution.workflow_version,
            },
        )

    def _determine_task_type(self, intent: Intent) -> TaskType:
        mapping = {
            IntentType.NEW_APPLICATION: TaskType.NEW_APPLICATION,
            IntentType.UPDATE_RECORD: TaskType.UPDATE_RECORD,
            IntentType.RENEWAL: TaskType.RENEWAL,
            IntentType.TRACK_APPLICATION: TaskType.TRACK_APPLICATION,
            IntentType.RAISE_GRIEVANCE: TaskType.RAISE_GRIEVANCE,
            IntentType.ELIGIBILITY_CHECK: TaskType.CHECK_ELIGIBILITY,
            IntentType.SERVICE_DISCOVERY: TaskType.DISCOVER_SERVICE,
            IntentType.DOCUMENT_REQUIREMENTS: TaskType.DISCOVER_SERVICE,
            IntentType.GENERAL_SERVICE_INFORMATION: TaskType.DISCOVER_SERVICE,
        }
        return mapping.get(intent.intent, TaskType.OTHER)

    def _parse_capabilities(self, capabilities: List[str]) -> List[ServiceCapability]:
        result = []
        for cap_str in capabilities:
            try:
                result.append(ServiceCapability(cap_str))
            except ValueError:
                continue
        return result

    def _build_steps(
        self,
        task_type: TaskType,
        capabilities: List[ServiceCapability],
        intent: Intent,
    ) -> List[WorkflowStep]:
        steps: List[WorkflowStep] = []

        if ServiceCapability.DISCOVER in capabilities:
            steps.append(WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Discover and verify the official government portal",
            ))

        if ServiceCapability.DOCUMENT_REQUIREMENTS in capabilities:
            steps.append(WorkflowStep(
                id="requirements",
                type=StepType.GET_REQUIREMENTS,
                description="Get service requirements and document checklist",
                dependencies=["discover"] if steps else [],
            ))

        if ServiceCapability.ELIGIBILITY_CHECK in capabilities:
            steps.append(WorkflowStep(
                id="eligibility",
                type=StepType.CHECK_ELIGIBILITY,
                description="Check applicant eligibility for the service",
                dependencies=["discover"] if steps else [],
            ))

        if task_type in (TaskType.NEW_APPLICATION, TaskType.UPDATE_RECORD, TaskType.RENEWAL):
            if ServiceCapability.DOCUMENT_REQUIREMENTS in capabilities:
                steps.append(WorkflowStep(
                    id="validate_docs",
                    type=StepType.VALIDATE_DOCUMENTS,
                    description="Validate and verify required documents",
                    dependencies=["requirements"],
                ))

            steps.append(WorkflowStep(
                id="prepare",
                type=StepType.PREPARE_APPLICATION,
                description="Prepare application data for submission",
                dependencies=["validate_docs"] if any(s.id == "validate_docs" for s in steps) else ["discover"],
            ))

            if task_type in (TaskType.NEW_APPLICATION, TaskType.RENEWAL):
                steps.append(WorkflowStep(
                    id="browser",
                    type=StepType.BROWSER_EXECUTION,
                    description="Execute form filling and submission on government portal",
                    dependencies=["prepare"],
                    timeout_seconds=600,
                ))

            steps.append(WorkflowStep(
                id="review",
                type=StepType.HUMAN_REVIEW,
                description="Review application before final submission",
                dependencies=["browser"] if any(s.id == "browser" for s in steps) else ["prepare"],
                requires_approval=True,
            ))

            steps.append(WorkflowStep(
                id="submit",
                type=StepType.SUBMIT,
                description="Submit the application to the government portal",
                dependencies=["review"],
                requires_approval=True,
                retry_policy=RetryPolicy(max_retries=0, retryable=False),
            ))

        elif task_type == TaskType.TRACK_APPLICATION:
            steps.append(WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Navigate to portal and check application status",
                dependencies=["discover"] if any(s.id == "discover" for s in steps) else [],
            ))
            steps.append(WorkflowStep(
                id="extract",
                type=StepType.EXTRACT_DATA,
                description="Extract application status and timeline data",
                dependencies=["browser"],
            ))

        elif task_type == TaskType.RAISE_GRIEVANCE:
            steps.append(WorkflowStep(
                id="prepare",
                type=StepType.PREPARE_APPLICATION,
                description="Prepare grievance details",
                dependencies=["discover"] if any(s.id == "discover" for s in steps) else [],
            ))
            steps.append(WorkflowStep(
                id="review",
                type=StepType.HUMAN_REVIEW,
                description="Review grievance before submission",
                dependencies=["prepare"],
                requires_approval=True,
            ))
            steps.append(WorkflowStep(
                id="submit",
                type=StepType.SUBMIT,
                description="Submit the grievance",
                dependencies=["review"],
                requires_approval=True,
                retry_policy=RetryPolicy(max_retries=0, retryable=False),
            ))

        steps.append(WorkflowStep(
            id="complete",
            type=StepType.COMPLETE,
            description="Mark task as completed and record result",
            dependencies=[s.id for s in steps if s.type != StepType.COMPLETE],
        ))

        return steps
