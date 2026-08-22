from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from packages.agent.orchestrator import AgentOrchestrator
from packages.agent.models.tasks import AgentTask, TaskStatus, AgentState
from packages.services.intent.models import IntentContext, Language

router = APIRouter(prefix="/agent", tags=["agent"])

_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


def set_orchestrator(orchestrator: AgentOrchestrator) -> None:
    global _orchestrator
    _orchestrator = orchestrator


class AgentContextRequest(BaseModel):
    language: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class AgentProcessRequest(BaseModel):
    message: str = Field(..., description="Natural language message from the user")
    user_id: str = Field(..., description="User ID")
    context: Optional[AgentContextRequest] = None


class AgentTaskResponse(BaseModel):
    task_id: str
    user_id: str
    original_request: str
    task_type: str
    service_id: Optional[str] = None
    state: str
    status: str
    error: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class AgentApproveRequest(BaseModel):
    approval_id: str = Field(..., description="Approval ID to approve")


class AgentApproveResponse(BaseModel):
    success: bool
    message: str


class AgentCancelResponse(BaseModel):
    success: bool
    message: str


@router.post("/process", response_model=AgentTaskResponse)
async def process_message(request: AgentProcessRequest):
    """Process a user message through the full agent pipeline."""
    orchestrator = get_orchestrator()

    context = None
    if request.context:
        lang = None
        if request.context.language:
            try:
                lang = Language(request.context.language)
            except ValueError:
                pass

        context = IntentContext(
            language=lang,
            country=request.context.country,
            state=request.context.state,
            district=request.context.district,
        )

    task = await orchestrator.process_request(
        message=request.message,
        user_id=request.user_id,
        context=context,
    )

    return AgentTaskResponse(
        task_id=task.task_id,
        user_id=task.user_id,
        original_request=task.original_request,
        task_type=task.task_type.value,
        service_id=task.service_id,
        state=task.state.value,
        status=task.status.value,
        error=task.error,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.post("/{task_id}/approve", response_model=AgentApproveResponse)
async def approve_task(task_id: str, request: AgentApproveRequest):
    """Approve a pending step in a task."""
    orchestrator = get_orchestrator()

    task = AgentTask(
        task_id=task_id,
        user_id="",
        original_request="",
    )
    task.status = TaskStatus.WAITING_FOR_APPROVAL
    task.state = AgentState.WAITING_FOR_APPROVAL

    success = await orchestrator.approve_step(task, request.approval_id)

    if not success:
        raise HTTPException(status_code=404, detail="Approval not found or expired")

    return AgentApproveResponse(
        success=True,
        message="Approval granted",
    )


@router.post("/{task_id}/cancel", response_model=AgentCancelResponse)
async def cancel_task(task_id: str):
    """Cancel an active task."""
    orchestrator = get_orchestrator()

    task = AgentTask(
        task_id=task_id,
        user_id="",
        original_request="",
    )

    await orchestrator.cancel_task(task)

    return AgentCancelResponse(
        success=True,
        message="Task cancelled",
    )
