from typing import Any

from fastapi import APIRouter, Query
from packages.services import ServiceResolver, get_registry
from pydantic import BaseModel, Field

router = APIRouter(prefix="/services", tags=["services"])


class ServiceMetadataResponse(BaseModel):
    service_id: str
    display_name: str
    description: str
    department: str
    jurisdiction: str
    official_portal: str
    capabilities: list[str]
    required_documents: list[dict[str, Any]]
    workflow_version: str
    enabled: bool
    estimated_processing_time: str | None = None
    fees: str | None = None


class ServiceListResponse(BaseModel):
    services: list[ServiceMetadataResponse]
    total: int


class ServiceResolveRequest(BaseModel):
    service_query: str = Field(..., description="Natural language query like 'income certificate'")
    jurisdiction: str | None = Field(None, description="Optional jurisdiction filter")
    capability: str | None = Field(None, description="Optional capability filter")


class ServiceResolveResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


class WorkflowPlanRequest(BaseModel):
    operation: str = Field(..., description="Operation like 'new_application', 'track_application'")


class WorkflowPlanResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


@router.get("", response_model=ServiceListResponse)
async def list_services():
    """List all registered government services."""
    registry = get_registry()
    services = registry.list_services()
    return ServiceListResponse(
        services=[
            ServiceMetadataResponse(
                service_id=s.service_id,
                display_name=s.display_name,
                description=s.description,
                department=s.department,
                jurisdiction=s.jurisdiction,
                official_portal=s.official_portal,
                capabilities=[c.value for c in s.capabilities],
                required_documents=[
                    {
                        "document_type": doc.document_type,
                        "display_name": doc.display_name,
                        "mandatory": doc.mandatory,
                    }
                    for doc in s.required_documents
                ],
                workflow_version=s.workflow_version,
                enabled=s.enabled,
                estimated_processing_time=s.estimated_processing_time,
                fees=s.fees,
            )
            for s in services
        ],
        total=len(services),
    )


@router.get("/search", response_model=ServiceListResponse)
async def search_services(q: str = Query(..., description="Search query")):
    """Search services by name, description, or department."""
    registry = get_registry()
    adapters = registry.find_services(q)
    return ServiceListResponse(
        services=[
            ServiceMetadataResponse(
                service_id=a.metadata().service_id,
                display_name=a.metadata().display_name,
                description=a.metadata().description,
                department=a.metadata().department,
                jurisdiction=a.metadata().jurisdiction,
                official_portal=a.metadata().official_portal,
                capabilities=[c.value for c in a.metadata().capabilities],
                required_documents=[
                    {
                        "document_type": doc.document_type,
                        "display_name": doc.display_name,
                        "mandatory": doc.mandatory,
                    }
                    for doc in a.metadata().required_documents
                ],
                workflow_version=a.metadata().workflow_version,
                enabled=a.metadata().enabled,
                estimated_processing_time=a.metadata().estimated_processing_time,
                fees=a.metadata().fees,
            )
            for a in adapters
        ],
        total=len(adapters),
    )


@router.get("/{service_id}", response_model=ServiceMetadataResponse)
async def get_service(service_id: str):
    """Get metadata for a specific service."""
    registry = get_registry()
    adapter = registry.get_service(service_id)
    if not adapter:
        return {"error": "Service not found"}
    s = adapter.metadata()
    return ServiceMetadataResponse(
        service_id=s.service_id,
        display_name=s.display_name,
        description=s.description,
        department=s.department,
        jurisdiction=s.jurisdiction,
        official_portal=s.official_portal,
        capabilities=[c.value for c in s.capabilities],
        required_documents=[
            {
                "document_type": doc.document_type,
                "display_name": doc.display_name,
                "mandatory": doc.mandatory,
            }
            for doc in s.required_documents
        ],
        workflow_version=s.workflow_version,
        enabled=s.enabled,
        estimated_processing_time=s.estimated_processing_time,
        fees=s.fees,
    )


@router.get("/{service_id}/capabilities")
async def get_service_capabilities(service_id: str):
    """Get capabilities for a specific service."""
    registry = get_registry()
    adapter = registry.get_service(service_id)
    if not adapter:
        return {"error": "Service not found"}
    return {
        "service_id": service_id,
        "capabilities": [c.value for c in adapter.get_capabilities()],
    }


@router.post("/resolve", response_model=ServiceResolveResponse)
async def resolve_service(request: ServiceResolveRequest):
    """Resolve a natural language query to a service."""
    resolver = ServiceResolver()
    result = await resolver.resolve(
        service_query=request.service_query,
        jurisdiction=request.jurisdiction,
        capability=request.capability,
    )
    return ServiceResolveResponse(
        success=result.success,
        data=result.data,
        error=result.error.model_dump() if result.error else None,
    )


@router.post("/{service_id}/plan", response_model=WorkflowPlanResponse)
async def get_workflow_plan(service_id: str, request: WorkflowPlanRequest):
    """Get workflow plan for a service operation."""
    resolver = ServiceResolver()
    result = await resolver.get_workflow_plan(service_id, request.operation)
    return WorkflowPlanResponse(
        success=result.success,
        data=result.data,
        error=result.error.model_dump() if result.error else None,
    )
