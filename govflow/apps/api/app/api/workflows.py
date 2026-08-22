"""Workflow API endpoints."""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.repositories.workflow import WorkflowRepository
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowExploreRequest,
    WorkflowExploreResponse,
    WorkflowInvalidateRequest,
    WorkflowRead,
    WorkflowStatusResponse,
    WorkflowUpdate,
)
from app.services.workflow_memory.service import WorkflowMemoryService

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _get_memory_service(db: AsyncSession) -> WorkflowMemoryService:
    repo = WorkflowRepository(db)
    return WorkflowMemoryService(repository=repo)


@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    service = _get_memory_service(db)
    raw = await service.get_raw(UUID(workflow_id))
    if not raw:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowRead.model_validate(raw)


@router.get("/service/{service_id}", response_model=List[WorkflowRead])
async def list_service_workflows(service_id: str, db: AsyncSession = Depends(get_db)):
    service = _get_memory_service(db)
    workflows = await service.search(service_id=service_id)
    raw_workflows = []
    for wf in workflows:
        if wf.workflow_id:
            raw = await service.get_raw(UUID(wf.workflow_id))
            if raw:
                raw_workflows.append(raw)
    return [WorkflowRead.model_validate(w) for w in raw_workflows]


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def workflow_status(workflow_id: str, db: AsyncSession = Depends(get_db)):
    service = _get_memory_service(db)
    raw = await service.get_raw(UUID(workflow_id))
    if not raw:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowStatusResponse(
        workflow_id=raw.id,
        status=raw.status,
        confidence=raw.confidence,
        execution_count=raw.execution_count or 0,
        success_count=raw.success_count or 0,
        failure_count=raw.failure_count or 0,
        recovery_count=raw.recovery_count or 0,
        last_verified_at=raw.last_verified_at,
        last_used_at=raw.last_used_at,
    )


@router.post("", response_model=WorkflowRead)
async def create_workflow(request: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    from app.models.workflow import Workflow
    from datetime import datetime, timezone

    service = _get_memory_service(db)
    workflow = Workflow(
        service_id=request.service_id,
        jurisdiction_id=request.jurisdiction_id,
        workflow_version=request.workflow_version,
        status="draft",
        source=request.source,
        workflow_definition=request.workflow_definition,
        confidence=request.confidence,
    )
    saved = await service._repo.create(workflow)
    logger.info("workflow_api_created", workflow_id=str(saved.id))
    return WorkflowRead.model_validate(saved)


@router.put("/{workflow_id}", response_model=WorkflowRead)
async def update_workflow(
    workflow_id: str, request: WorkflowUpdate, db: AsyncSession = Depends(get_db)
):
    service = _get_memory_service(db)
    update_kwargs = {}
    if request.workflow_version is not None:
        update_kwargs["workflow_version"] = request.workflow_version
    if request.status is not None:
        update_kwargs["status"] = request.status
    if request.workflow_definition is not None:
        update_kwargs["workflow_definition"] = request.workflow_definition
    if request.confidence is not None:
        update_kwargs["confidence"] = request.confidence
    if request.source is not None:
        update_kwargs["source"] = request.source

    updated = await service._repo.update(UUID(workflow_id), **update_kwargs)
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowRead.model_validate(updated)


@router.post("/{workflow_id}/invalidate")
async def invalidate_workflow(
    workflow_id: str, request: WorkflowInvalidateRequest, db: AsyncSession = Depends(get_db)
):
    service = _get_memory_service(db)
    updated = await service.mark_outdated(UUID(workflow_id), reason=request.reason)
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "outdated", "workflow_id": workflow_id}


@router.post("/explore", response_model=WorkflowExploreResponse)
async def trigger_exploration(request: WorkflowExploreRequest):
    import uuid
    task_id = str(uuid.uuid4())
    logger.info(
        "exploration_triggered",
        task_id=task_id,
        service_id=str(request.service_id),
        url=request.url,
    )
    return WorkflowExploreResponse(
        task_id=task_id,
        status="queued",
        message=f"Exploration of {request.url} has been queued",
    )
