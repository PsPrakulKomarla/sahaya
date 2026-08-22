from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.models.user import User
from app.models.grievance import Grievance, GrievanceStatus
from app.schemas.grievance import GrievanceCreate, GrievanceRead, GrievanceUpdate
from app.repositories.grievance import GrievanceRepository
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/grievances", tags=["grievances"])


class GrievanceDraftRequest(BaseModel):
    service_id: str
    user_issue: str
    language: str = "en"
    application_id: Optional[UUID] = None
    jurisdiction: Optional[str] = None


class GrievanceDraftResponse(BaseModel):
    grievance_id: UUID
    subject: str
    description: str
    category: str
    status: str
    application_reference: Optional[str] = None
    facts: List[Dict[str, Any]] = []
    attachments: List[str] = []


class GrievanceUpdateRequest(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    jurisdiction: Optional[str] = None
    facts: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[str]] = None


class ApprovalRequest(BaseModel):
    approval_id: str


class TrackResponse(BaseModel):
    official_reference_number: str
    source_status: str
    normalized_status: str
    status_changed: bool
    raw: Dict[str, Any] = {}


def get_grievance_repo(session: AsyncSession = Depends(get_session)) -> GrievanceRepository:
    return GrievanceRepository(session)


@router.post("", response_model=GrievanceRead, status_code=status.HTTP_201_CREATED)
async def create_grievance(
    request: GrievanceCreate,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Create a new grievance."""
    grievance = Grievance(
        user_id=current_user.id,
        application_id=request.application_id,
        service_id=request.service_id,
        jurisdiction_id=request.jurisdiction_id,
        status=GrievanceStatus.DRAFT,
        subject=request.subject,
        description=request.description,
        metadata_extra=request.metadata_extra,
    )
    return await repo.create(grievance)


@router.get("", response_model=List[GrievanceRead])
async def list_grievances(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """List all grievances for the current user."""
    return await repo.list_by_user(current_user.id, skip=skip, limit=limit)


@router.get("/{grievance_id}", response_model=GrievanceRead)
async def get_grievance(
    grievance_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Get a specific grievance by ID."""
    grievance = await repo.get_by_id(grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this grievance")
    return grievance


@router.patch("/{grievance_id}", response_model=GrievanceRead)
async def update_grievance(
    grievance_id: UUID,
    request: GrievanceUpdate,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Update a grievance (only in DRAFT state)."""
    grievance = await repo.get_by_id(grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this grievance")

    update_data = request.model_dump(exclude_unset=True)
    return await repo.update(grievance_id, **update_data)


@router.post("/{grievance_id}/review", status_code=status.HTTP_202_ACCEPTED)
async def request_review(
    grievance_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Request human review for grievance submission."""
    grievance = await repo.get_by_id(grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if grievance.status not in (GrievanceStatus.DRAFT, GrievanceStatus.PREPARING):
        raise HTTPException(status_code=400, detail="Grievance not in a reviewable state")

    grievance.status = GrievanceStatus.READY_FOR_REVIEW
    grievance.updated_at = datetime.utcnow()
    return await repo.save(grievance)


@router.post("/{grievance_id}/approve")
async def approve_grievance(
    grievance_id: UUID,
    request: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Approve grievance for submission."""
    grievance = await repo.get_by_id(grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # In a real implementation, validate approval through approval service
    grievance.status = GrievanceStatus.SUBMITTED
    grievance.submitted_at = datetime.utcnow()
    grievance.updated_at = datetime.utcnow()
    return await repo.save(grievance)


@router.post("/{grievance_id}/reject")
async def reject_grievance(
    grievance_id: UUID,
    request: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Reject grievance approval."""
    grievance = await repo.get_by_id(grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    grievance.status = GrievanceStatus.READY_FOR_REVIEW
    grievance.updated_at = datetime.utcnow()
    return await repo.save(grievance)


@router.post("/{grievance_id}/track", response_model=TrackResponse)
async def track_grievance(
    grievance_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: GrievanceRepository = Depends(get_grievance_repo),
):
    """Track grievance status."""
    grievance = await repo.get_by_id(grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    if grievance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # In a real implementation, this would call the tracking service
    return TrackResponse(
        official_reference_number=grievance.official_reference_number or "",
        source_status=grievance.source_status or "unknown",
        normalized_status=grievance.status,
        status_changed=False,
    )