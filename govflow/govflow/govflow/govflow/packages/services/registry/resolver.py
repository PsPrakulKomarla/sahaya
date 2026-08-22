from typing import Optional, Dict, Any
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import ServiceResponse, ServiceError
from packages.services.registry.registry import get_registry


class ServiceResolver:
    """Resolves user intent to the correct service adapter.

    Sits between the AI planner and Service Registry.
    The AI planner should NOT directly import individual government adapters.
    """

    def __init__(self):
        self.registry = get_registry()

    async def resolve(
        self,
        service_query: str,
        jurisdiction: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> ServiceResponse:
        """Resolve a user query to a service adapter.

        Args:
            service_query: Natural language query like "income certificate"
            jurisdiction: Optional jurisdiction filter like "Karnataka"
            capability: Optional capability filter like "new_application"

        Returns:
            ServiceResponse with resolved service or error
        """
        adapters = self.registry.find_services(service_query)

        if not adapters:
            return ServiceResponse(
                success=False,
                error=ServiceError(
                    error_code="SERVICE_NOT_FOUND",
                    message=f"No service found matching '{service_query}'",
                    recoverable=True,
                    suggested_action="REFINE_QUERY",
                ),
            )

        if jurisdiction:
            jurisdiction_lower = jurisdiction.lower()
            adapters = [
                a for a in adapters
                if jurisdiction_lower in a.metadata().jurisdiction.lower()
            ]
            if not adapters:
                return ServiceResponse(
                    success=False,
                    error=ServiceError(
                        error_code="JURISDICTION_NOT_AVAILABLE",
                        message=f"Service '{service_query}' is not available in jurisdiction '{jurisdiction}'",
                        recoverable=True,
                        suggested_action="REQUEST_JURISDICTION",
                    ),
                )

        if capability:
            try:
                cap = capability.lower()
                adapters = [
                    a for a in adapters
                    if any(c.value == cap for c in a.get_capabilities())
                ]
                if not adapters:
                    return ServiceResponse(
                        success=False,
                        error=ServiceError(
                            error_code="CAPABILITY_NOT_AVAILABLE",
                            message=f"Capability '{capability}' is not available for '{service_query}'",
                            recoverable=True,
                            suggested_action="CHECK_CAPABILITIES",
                        ),
                    )
            except Exception:
                pass

        adapter = adapters[0]
        metadata = adapter.metadata()

        return ServiceResponse(
            success=True,
            data={
                "service_id": metadata.service_id,
                "display_name": metadata.display_name,
                "description": metadata.description,
                "department": metadata.department,
                "jurisdiction": metadata.jurisdiction,
                "official_portal": metadata.official_portal,
                "capabilities": [c.value for c in metadata.capabilities],
                "required_documents": [
                    {
                        "document_type": doc.document_type,
                        "display_name": doc.display_name,
                        "mandatory": doc.mandatory,
                    }
                    for doc in metadata.required_documents
                ],
                "workflow_version": metadata.workflow_version,
                "estimated_processing_time": metadata.estimated_processing_time,
                "fees": metadata.fees,
            },
        )

    async def get_workflow_plan(self, service_id: str, operation: str) -> ServiceResponse:
        """Get workflow plan for a specific service operation."""
        adapter = self.registry.get_service(service_id)
        if not adapter:
            return ServiceResponse(
                success=False,
                error=ServiceError(
                    error_code="SERVICE_NOT_FOUND",
                    message=f"Service '{service_id}' not found",
                    recoverable=False,
                ),
            )

        return await adapter.get_workflow_plan(operation)

    async def check_eligibility(self, service_id: str, user_data: Dict[str, Any]) -> ServiceResponse:
        """Check eligibility for a specific service."""
        adapter = self.registry.get_service(service_id)
        if not adapter:
            return ServiceResponse(
                success=False,
                error=ServiceError(
                    error_code="SERVICE_NOT_FOUND",
                    message=f"Service '{service_id}' not found",
                    recoverable=False,
                ),
            )

        return await adapter.check_eligibility(user_data)