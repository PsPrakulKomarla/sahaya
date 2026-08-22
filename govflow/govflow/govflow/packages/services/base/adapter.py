from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from packages.services.base.models import (
    ServiceMetadata,
    ServiceCapability,
    ServiceResponse,
    EligibilityCriteria,
    DocumentRequirement,
    WorkflowStep,
    CapabilityNotSupportedError,
)


class GovernmentServiceAdapter(ABC):
    """Base interface for all government service adapters.

    Each adapter implements the contract for a specific government service.
    Not every adapter must implement every operation.
    Unsupported operations should return a structured "capability not supported" response.
    """

    @abstractmethod
    def metadata(self) -> ServiceMetadata:
        """Return service metadata including capabilities, requirements, etc."""
        pass

    def get_capabilities(self) -> List[ServiceCapability]:
        """Return list of supported capabilities."""
        return self.metadata().capabilities

    def supports_capability(self, capability: ServiceCapability) -> bool:
        """Check if this adapter supports a specific capability."""
        return capability in self.get_capabilities()

    def _require_capability(self, capability: ServiceCapability) -> None:
        """Raise CapabilityNotSupportedError if capability is not supported."""
        if not self.supports_capability(capability):
            raise CapabilityNotSupportedError(capability, self.metadata().service_id)

    @abstractmethod
    async def discover(self, query: str, jurisdiction: Optional[str] = None) -> ServiceResponse:
        """Discover and return service information based on user query."""
        pass

    async def check_eligibility(self, user_data: Dict[str, Any]) -> ServiceResponse:
        """Check if user is eligible for this service."""
        self._require_capability(ServiceCapability.ELIGIBILITY_CHECK)
        return ServiceResponse(
            success=False,
            error=CapabilityNotSupportedError(ServiceCapability.ELIGIBILITY_CHECK, self.metadata().service_id),
        )

    async def get_document_requirements(self) -> ServiceResponse:
        """Return list of required documents for this service."""
        self._require_capability(ServiceCapability.DOCUMENT_REQUIREMENTS)
        docs = self.metadata().required_documents
        return ServiceResponse(
            success=True,
            data={"documents": [doc.model_dump() for doc in docs]},
        )

    async def create_application(self, application_data: Dict[str, Any]) -> ServiceResponse:
        """Create a new application for this service."""
        self._require_capability(ServiceCapability.NEW_APPLICATION)
        return ServiceResponse(
            success=False,
            error=CapabilityNotSupportedError(ServiceCapability.NEW_APPLICATION, self.metadata().service_id),
        )

    async def update_record(self, update_data: Dict[str, Any]) -> ServiceResponse:
        """Update an existing government record."""
        self._require_capability(ServiceCapability.UPDATE_RECORD)
        return ServiceResponse(
            success=False,
            error=CapabilityNotSupportedError(ServiceCapability.UPDATE_RECORD, self.metadata().service_id),
        )

    async def track_application(self, reference_number: str) -> ServiceResponse:
        """Track status of an existing application."""
        self._require_capability(ServiceCapability.TRACK_APPLICATION)
        return ServiceResponse(
            success=False,
            error=CapabilityNotSupportedError(ServiceCapability.TRACK_APPLICATION, self.metadata().service_id),
        )

    async def create_grievance(self, grievance_data: Dict[str, Any]) -> ServiceResponse:
        """Create a grievance/complaint related to this service."""
        self._require_capability(ServiceCapability.RAISE_GRIEVANCE)
        return ServiceResponse(
            success=False,
            error=CapabilityNotSupportedError(ServiceCapability.RAISE_GRIEVANCE, self.metadata().service_id),
        )

    async def get_workflow_plan(self, operation: str) -> ServiceResponse:
        """Return structured workflow plan for an operation."""
        steps = self._generate_workflow_steps(operation)
        return ServiceResponse(
            success=True,
            data={
                "service": self.metadata().service_id,
                "operation": operation,
                "steps": [step.model_dump() for step in steps],
            },
        )

    def _generate_workflow_steps(self, operation: str) -> List[WorkflowStep]:
        """Generate workflow steps for an operation. Override in subclasses for custom workflows."""
        return [
            WorkflowStep(
                id="discover_portal",
                action="DISCOVER_OFFICIAL_PORTAL",
                description="Identify and verify the official government portal",
            ),
            WorkflowStep(
                id="requirements",
                action="GET_REQUIREMENTS",
                description="Gather service requirements and eligibility criteria",
            ),
            WorkflowStep(
                id="documents",
                action="VALIDATE_DOCUMENTS",
                description="Validate and verify required documents",
            ),
            WorkflowStep(
                id="application",
                action="START_APPLICATION",
                description="Begin the application process",
            ),
            WorkflowStep(
                id="review",
                action="HUMAN_REVIEW",
                description="Review application before submission",
                requires_human_approval=True,
            ),
            WorkflowStep(
                id="submit",
                action="SUBMIT_APPLICATION",
                description="Submit the application to the government portal",
                requires_human_approval=True,
            ),
        ]