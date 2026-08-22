import uuid
from typing import Any, Optional, List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/applications", tags=["applications"])

_applications_store: Dict[str, Dict[str, Any]] = {}
_application_timelines: Dict[str, List[Dict[str, Any]]] = {}


class ApplicationCreateRequest(BaseModel):
    user_id: str
    service_id: str
    jurisdiction_id: Optional[str] = None
    form_data: Dict[str, Any] = {}
    document_ids: List[str] = []


class ApplicationUpdateRequest(BaseModel):
    form_data: Optional[Dict[str, Any]] = None
    document_ids: Optional[List[str]] = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    service_id: str
    jurisdiction_id: Optional[str] = None
    status: str
    reference_number: Optional[str] = None
    form_data: Dict[str, Any] = {}
    document_ids: List[str] = []
    submitted_at: Optional[str] = None
    next_action: Optional[str] = None
    created_at: str
    updated_at: str


class ApplicationListResponse(BaseModel):
    applications: List[ApplicationResponse]
    total: int


class ApplicationValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]
    missing_fields: List[str]


class TimelineEventResponse(BaseModel):
    id: str
    application_id: str
    event_type: str
    status: Optional[str] = None
    note: Optional[str] = None
    timestamp: str


class TimelineResponse(BaseModel):
    events: List[TimelineEventResponse]
    total: int


@router.post("", response_model=ApplicationResponse)
async def create_application(request: ApplicationCreateRequest):
    """Create a new application draft."""
    from packages.applications.application_service import ApplicationService

    service = ApplicationService()
    draft = service.create_draft(
        user_id=request.user_id,
        service_id=request.service_id,
        form_data=request.form_data,
        document_ids=request.document_ids,
        jurisdiction=request.jurisdiction_id,
    )
    _applications_store[draft["id"]] = draft
    _application_timelines[draft["id"]] = [
        service.create_timeline_event(draft["id"], "APPLICATION_CREATED", "draft", "Application draft created")
    ]
    return ApplicationResponse(**{k: v for k, v in draft.items() if k in ApplicationResponse.model_fields})


@router.get("", response_model=ApplicationListResponse)
async def list_applications(user_id: str, skip: int = 0, limit: int = 100):
    """List applications for a user."""
    user_apps = [a for a in _applications_store.values() if a["user_id"] == user_id]
    return ApplicationListResponse(
        applications=[
            ApplicationResponse(**{k: v for k, v in a.items() if k in ApplicationResponse.model_fields})
            for a in user_apps[skip:skip + limit]
        ],
        total=len(user_apps),
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str, user_id: str):
    """Get a specific application."""
    app = _applications_store.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return ApplicationResponse(**{k: v for k, v in app.items() if k in ApplicationResponse.model_fields})


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(application_id: str, request: ApplicationUpdateRequest, user_id: str):
    """Update an application draft."""
    app = _applications_store.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    from packages.applications.application_service import ApplicationService

    service = ApplicationService()
    updated = service.update_draft(app, form_data=request.form_data, document_ids=request.document_ids)
    _applications_store[application_id] = updated

    timeline = _application_timelines.get(application_id, [])
    timeline.append(service.create_timeline_event(application_id, "DRAFT_UPDATED", updated["status"]))
    _application_timelines[application_id] = timeline

    return ApplicationResponse(**{k: v for k, v in updated.items() if k in ApplicationResponse.model_fields})


@router.post("/{application_id}/validate", response_model=ApplicationValidationResponse)
async def validate_application(application_id: str, user_id: str):
    """Validate an application draft."""
    app = _applications_store.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    from packages.applications.application_service import ApplicationService

    service = ApplicationService()
    return service.validate_draft(app)


@router.post("/{application_id}/review")
async def review_application(application_id: str, user_id: str):
    """Mark application as ready for review."""
    app = _applications_store.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    from packages.applications.application_service import ApplicationService

    service = ApplicationService()
    result = service.mark_ready_for_review(app)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["validation"])

    _applications_store[application_id] = result["application"]
    timeline = _application_timelines.get(application_id, [])
    timeline.append(service.create_timeline_event(application_id, "REVIEW_REQUESTED", "ready_for_review"))
    _application_timelines[application_id] = timeline

    return {"success": True, "application": result["application"]}


@router.get("/{application_id}/timeline", response_model=TimelineResponse)
async def get_application_timeline(application_id: str, user_id: str):
    """Get application timeline events."""
    app = _applications_store.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    events = _application_timelines.get(application_id, [])
    return TimelineResponse(
        events=[TimelineEventResponse(**e) for e in events],
        total=len(events),
    )
