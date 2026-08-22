"""TaskPlanner converts intent + service resolution into a WorkflowPlan.

The planner operates on generic service capabilities — it does NOT depend on
specific service adapters (IncomeCertificate, BirthCertificate, etc.).
"""
from __future__ import annotations

from typing import List, Optional

from packages.agent.planner.models import RetryPolicy, StepType, WorkflowPlan, WorkflowStep
from packages.agent.errors import WorkflowInvalid
from packages.services.intent.models import Intent, IntentType
from packages.services.registry.models import ServiceResolution
from packages.services.base.models import ServiceCapability


class TaskPlanner:
    """Converts structured intent + service resolution into a WorkflowPlan.

    The planner maps IntentType + ServiceCapabilities to a sequence of
    WorkflowSteps. It does NOT contain service-specific logic.
    """

    INTENT_TO_CAPABILITY = {
        IntentType.NEW_APPLICATION: ServiceCapability.NEW_APPLICATION,
        IntentType.UPDATE_RECORD: ServiceCapability.UPDATE_RECORD,
        IntentType.RENEWAL: ServiceCapability.RENEW,
        IntentType.TRACK_APPLICATION: ServiceCapability.TRACK_APPLICATION,
        IntentType.RAISE_GRIEVANCE: ServiceCapability.RAISE_GRIEVANCE,
        IntentType.ELIGIBILITY_CHECK: ServiceCapability.ELIGIBILITY_CHECK,
        IntentType.DOCUMENT_REQUIREMENTS: ServiceCapability.DOCUMENT_REQUIREMENTS,
    }

    def plan(
        self,
        intent: Intent,
        resolution: ServiceResolution,
    ) -> WorkflowPlan:
        """Create a WorkflowPlan from intent and service resolution.

        Args:
            intent: The parsed user intent.
            resolution: The resolved service information.

        Returns:
            A complete WorkflowPlan with ordered steps.

        Raises:
            WorkflowInvalid: If the intent cannot be mapped to a plan.
        """
        intent_type = IntentType(intent.intent) if isinstance(intent.intent, str) else intent.intent

        if intent_type == IntentType.CLARIFICATION_REQUIRED:
            raise WorkflowInvalid("Cannot plan for clarification-required intent")

        if intent_type == IntentType.SERVICE_DISCOVERY:
            return self._plan_discovery(intent, resolution)

        if intent_type == IntentType.GENERAL_SERVICE_INFORMATION:
            return self._plan_discovery(intent, resolution)

        capability = self.INTENT_TO_CAPABILITY.get(intent_type)
        if capability is None:
            raise WorkflowInvalid(f"Unknown intent type: {intent_type}")

        steps = self._build_steps_for_capability(capability, resolution)

        return WorkflowPlan(
            task_type=intent_type.value,
            service_id=resolution.service_id or "unknown",
            steps=steps,
            metadata={
                "intent_confidence": intent.confidence,
                "resolution_confidence": resolution.confidence,
                "jurisdiction": resolution.jurisdiction.dict() if resolution.jurisdiction else {},
            },
        )

    def _build_steps_for_capability(
        self,
        capability: ServiceCapability,
        resolution: ServiceResolution,
    ) -> List[WorkflowStep]:
        """Build workflow steps based on the required capability."""
        builders = {
            ServiceCapability.NEW_APPLICATION: self._build_new_application_steps,
            ServiceCapability.UPDATE_RECORD: self._build_update_steps,
            ServiceCapability.RENEW: self._build_renewal_steps,
            ServiceCapability.TRACK_APPLICATION: self._build_tracking_steps,
            ServiceCapability.RAISE_GRIEVANCE: self._build_grievance_steps,
            ServiceCapability.ELIGIBILITY_CHECK: self._build_eligibility_steps,
            ServiceCapability.DOCUMENT_REQUIREMENTS: self._build_document_steps,
        }
        builder = builders.get(capability)
        if builder:
            return builder(resolution)
        return self._build_generic_steps(resolution)

    def _build_new_application_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate and verify the official government portal",
            ),
            WorkflowStep(
                id="requirements",
                type=StepType.GET_REQUIREMENTS,
                description="Gather service requirements and eligibility criteria",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="eligibility",
                type=StepType.CHECK_ELIGIBILITY,
                description="Verify user eligibility for this service",
                dependencies=["requirements"],
            ),
            WorkflowStep(
                id="documents",
                type=StepType.VALIDATE_DOCUMENTS,
                description="Validate and verify required documents",
                dependencies=["eligibility"],
            ),
            WorkflowStep(
                id="prepare",
                type=StepType.PREPARE_APPLICATION,
                description="Prepare application data from validated documents",
                dependencies=["documents"],
            ),
            WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Execute application on government portal via browser",
                dependencies=["prepare"],
            ),
            WorkflowStep(
                id="review",
                type=StepType.HUMAN_REVIEW,
                description="Review application before final submission",
                dependencies=["browser"],
                requires_approval=True,
            ),
            WorkflowStep(
                id="submit",
                type=StepType.SUBMIT,
                description="Submit the application to the government portal",
                dependencies=["review"],
                requires_approval=True,
                retry_policy=RetryPolicy(max_retries=0, retryable=False),
            ),
            WorkflowStep(
                id="track",
                type=StepType.TRACK_APPLICATION,
                description="Track application status after submission",
                dependencies=["submit"],
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Task completed successfully",
                dependencies=["track"],
            ),
        ]

    def _build_update_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate the government portal for record updates",
            ),
            WorkflowStep(
                id="requirements",
                type=StepType.GET_REQUIREMENTS,
                description="Determine what documents and data are needed",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="documents",
                type=StepType.VALIDATE_DOCUMENTS,
                description="Validate supporting documents for the update",
                dependencies=["requirements"],
            ),
            WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Navigate portal and perform record update",
                dependencies=["documents"],
            ),
            WorkflowStep(
                id="review",
                type=StepType.HUMAN_REVIEW,
                description="Review the update before submission",
                dependencies=["browser"],
                requires_approval=True,
            ),
            WorkflowStep(
                id="submit",
                type=StepType.SUBMIT,
                description="Submit the record update",
                dependencies=["review"],
                requires_approval=True,
                retry_policy=RetryPolicy(max_retries=0, retryable=False),
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Update completed successfully",
                dependencies=["submit"],
            ),
        ]

    def _build_renewal_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate the renewal portal",
            ),
            WorkflowStep(
                id="requirements",
                type=StepType.GET_REQUIREMENTS,
                description="Check renewal requirements and deadlines",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="eligibility",
                type=StepType.CHECK_ELIGIBILITY,
                description="Verify renewal eligibility",
                dependencies=["requirements"],
            ),
            WorkflowStep(
                id="documents",
                type=StepType.VALIDATE_DOCUMENTS,
                description="Validate documents for renewal",
                dependencies=["eligibility"],
            ),
            WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Execute renewal on government portal",
                dependencies=["documents"],
            ),
            WorkflowStep(
                id="review",
                type=StepType.HUMAN_REVIEW,
                description="Review renewal before submission",
                dependencies=["browser"],
                requires_approval=True,
            ),
            WorkflowStep(
                id="submit",
                type=StepType.SUBMIT,
                description="Submit the renewal",
                dependencies=["review"],
                requires_approval=True,
                retry_policy=RetryPolicy(max_retries=0, retryable=False),
            ),
            WorkflowStep(
                id="track",
                type=StepType.TRACK_APPLICATION,
                description="Track renewal status after submission",
                dependencies=["submit"],
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Renewal completed successfully",
                dependencies=["track"],
            ),
        ]

    def _build_tracking_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate the tracking portal",
            ),
            WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Navigate to tracking page and enter reference number",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="extract",
                type=StepType.EXTRACT_DATA,
                description="Extract application status from the portal",
                dependencies=["browser"],
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Tracking completed",
                dependencies=["extract"],
            ),
        ]

    def _build_grievance_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate the grievance portal",
            ),
            WorkflowStep(
                id="requirements",
                type=StepType.GET_REQUIREMENTS,
                description="Determine grievance filing requirements",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Navigate portal and file grievance",
                dependencies=["requirements"],
            ),
            WorkflowStep(
                id="review",
                type=StepType.HUMAN_REVIEW,
                description="Review grievance before submission",
                dependencies=["browser"],
                requires_approval=True,
            ),
            WorkflowStep(
                id="submit",
                type=StepType.SUBMIT,
                description="Submit the grievance",
                dependencies=["review"],
                requires_approval=True,
                retry_policy=RetryPolicy(max_retries=0, retryable=False),
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Grievance submitted successfully",
                dependencies=["submit"],
            ),
        ]

    def _build_eligibility_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate the eligibility information",
            ),
            WorkflowStep(
                id="eligibility",
                type=StepType.CHECK_ELIGIBILITY,
                description="Check eligibility criteria",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Eligibility check completed",
                dependencies=["eligibility"],
            ),
        ]

    def _build_document_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Locate document requirements",
            ),
            WorkflowStep(
                id="requirements",
                type=StepType.GET_REQUIREMENTS,
                description="Gather document requirements",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="documents",
                type=StepType.VALIDATE_DOCUMENTS,
                description="Validate provided documents against requirements",
                dependencies=["requirements"],
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Document validation completed",
                dependencies=["documents"],
            ),
        ]

    def _build_generic_steps(self, resolution: ServiceResolution) -> List[WorkflowStep]:
        return [
            WorkflowStep(
                id="discover",
                type=StepType.DISCOVER_SERVICE,
                description="Discover the service",
            ),
            WorkflowStep(
                id="browser",
                type=StepType.BROWSER_EXECUTION,
                description="Execute the required browser actions",
                dependencies=["discover"],
            ),
            WorkflowStep(
                id="complete",
                type=StepType.COMPLETE,
                description="Task completed",
                dependencies=["browser"],
            ),
        ]

    def _plan_discovery(self, intent: Intent, resolution: ServiceResolution) -> WorkflowPlan:
        return WorkflowPlan(
            task_type=intent.intent.value if isinstance(intent.intent, IntentType) else intent.intent,
            service_id=resolution.service_id or "unknown",
            steps=[
                WorkflowStep(
                    id="discover",
                    type=StepType.DISCOVER_SERVICE,
                    description="Discover available services",
                ),
                WorkflowStep(
                    id="complete",
                    type=StepType.COMPLETE,
                    description="Discovery completed",
                    dependencies=["discover"],
                ),
            ],
        )
