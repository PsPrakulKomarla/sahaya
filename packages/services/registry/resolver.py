from typing import Optional, Dict, Any, List
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import ServiceResponse, ServiceError, ServiceCapability
from packages.services.registry.registry import get_registry
from packages.services.registry.models import (
    ResolutionStatus,
    ServiceResolution,
    ResolutionJurisdiction,
)
from packages.services.intent.models import Intent, IntentType


class ServiceResolver:
    """Resolves user intent to the correct service adapter.

    Sits between the AI planner and Service Registry.
    The AI planner should NOT directly import individual government adapters.

    This resolver supports both the legacy query-based interface and the new
    intent-based interface.
    """

    CAPABILITY_MAP = {
        IntentType.SERVICE_DISCOVERY: ServiceCapability.DISCOVER,
        IntentType.ELIGIBILITY_CHECK: ServiceCapability.ELIGIBILITY_CHECK,
        IntentType.DOCUMENT_REQUIREMENTS: ServiceCapability.DOCUMENT_REQUIREMENTS,
        IntentType.NEW_APPLICATION: ServiceCapability.NEW_APPLICATION,
        IntentType.UPDATE_RECORD: ServiceCapability.UPDATE_RECORD,
        IntentType.RENEWAL: ServiceCapability.RENEW,
        IntentType.TRACK_APPLICATION: ServiceCapability.TRACK_APPLICATION,
        IntentType.RAISE_GRIEVANCE: ServiceCapability.RAISE_GRIEVANCE,
    }

    def __init__(self):
        self.registry = get_registry()

    async def resolve_intent(self, intent: Intent) -> ServiceResolution:
        """Resolve a structured intent to a service.

        Args:
            intent: The parsed intent from the IntentEngine.

        Returns:
            A ServiceResolution with the resolved service or error information.
        """
        if not intent.service_query and intent.intent not in [
            IntentType.SERVICE_DISCOVERY,
            IntentType.GENERAL_SERVICE_INFORMATION,
        ]:
            return ServiceResolution(
                status=ResolutionStatus.INVALID_REQUEST,
                reason="No service query provided",
                confidence=0.0,
                clarification_questions=["Which government service are you looking for?"],
            )

        state = intent.jurisdiction.state
        if state:
            candidates = self.registry.find_by_jurisdiction(state)
        else:
            candidates = list(self.registry._adapters.values())

        if not candidates:
            candidates = list(self.registry._adapters.values())

        matched = []
        for adapter in candidates:
            metadata = adapter.metadata()
            score = self._calculate_match_score(intent.service_query, metadata)
            if score > 0:
                matched.append((adapter, score, metadata))

        if not matched:
            return ServiceResolution(
                status=ResolutionStatus.NOT_FOUND,
                reason=f"No service found matching '{intent.service_query}'",
                confidence=0.0,
                clarification_questions=["Could you rephrase your request or specify the service you need?"],
            )

        matched.sort(key=lambda x: x[1], reverse=True)

        if len(matched) > 1 and matched[0][1] - matched[1][1] < 0.1:
            ambiguous_services = [m[2].display_name for m in matched[:3]]
            return ServiceResolution(
                status=ResolutionStatus.AMBIGUOUS,
                reason="Multiple services match your request",
                confidence=matched[0][1],
                clarification_questions=[
                    f"Did you mean: {', '.join(ambiguous_services)}?"
                ],
            )

        adapter, score, metadata = matched[0]

        if not metadata.enabled:
            return ServiceResolution(
                status=ResolutionStatus.SERVICE_DISABLED,
                service_id=metadata.service_id,
                service_name=metadata.display_name,
                reason="This service is currently disabled",
                confidence=score,
            )

        requested_capability = self.CAPABILITY_MAP.get(intent.intent)
        if requested_capability and requested_capability not in metadata.capabilities:
            supported = [c.value for c in metadata.capabilities]
            return ServiceResolution(
                status=ResolutionStatus.CAPABILITY_UNSUPPORTED,
                service_id=metadata.service_id,
                service_name=metadata.display_name,
                operation=intent.operation,
                capabilities=supported,
                reason=f"The requested operation '{intent.intent}' is not supported for {metadata.display_name}",
                confidence=score,
                clarification_questions=[
                    f"{metadata.display_name} supports: {', '.join(supported)}"
                ],
            )

        jurisdiction = ResolutionJurisdiction(
            country=intent.jurisdiction.country or "India",
            state=state or metadata.jurisdiction,
            district=intent.jurisdiction.district,
        )

        if state and state.lower() != metadata.jurisdiction.lower():
            available_jurisdictions = self._get_available_jurisdictions(intent.service_query)
            if len(available_jurisdictions) > 1:
                return ServiceResolution(
                    status=ResolutionStatus.JURISDICTION_REQUIRED,
                    service_id=metadata.service_id,
                    service_name=metadata.display_name,
                    reason=f"Multiple jurisdictions available for {metadata.display_name}",
                    confidence=score,
                    clarification_questions=[
                        f"Which jurisdiction would you like? Available: {', '.join(available_jurisdictions)}"
                    ],
                )

        capabilities = [c.value for c in metadata.capabilities]

        return ServiceResolution(
            status=ResolutionStatus.RESOLVED,
            service_id=metadata.service_id,
            service_name=metadata.display_name,
            operation=intent.operation,
            jurisdiction=jurisdiction,
            capabilities=capabilities,
            workflow_version=metadata.workflow_version,
            confidence=score,
            metadata={
                "department": metadata.department,
                "official_portal": metadata.official_portal,
                "estimated_processing_time": metadata.estimated_processing_time,
                "fees": metadata.fees,
            },
        )

    async def resolve(
        self,
        service_query: str,
        jurisdiction: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> ServiceResponse:
        """Resolve a user query to a service adapter (legacy interface).

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

    def _calculate_match_score(self, query: str, metadata) -> float:
        """Calculate a match score between a query and service metadata."""
        query_lower = query.lower().strip()
        score = 0.0

        if query_lower == metadata.service_id.lower():
            score = max(score, 1.0)

        if query_lower == metadata.display_name.lower():
            score = max(score, 0.95)

        for alias in metadata.aliases:
            if query_lower == alias.lower():
                score = max(score, 0.9)
            elif query_lower in alias.lower() or alias.lower() in query_lower:
                score = max(score, 0.7)

        if query_lower in metadata.description.lower():
            score = max(score, 0.5)

        query_words = set(query_lower.split())
        display_words = set(metadata.display_name.lower().split())
        if query_words and display_words:
            overlap = query_words & display_words
            if overlap:
                word_score = len(overlap) / max(len(query_words), len(display_words))
                score = max(score, word_score * 0.6)

        return score

    def _get_available_jurisdictions(self, service_query: str) -> List[str]:
        """Get available jurisdictions for a service query."""
        adapters = self.registry.find_services(service_query)
        jurisdictions = list(set(a.metadata().jurisdiction for a in adapters))
        return jurisdictions
