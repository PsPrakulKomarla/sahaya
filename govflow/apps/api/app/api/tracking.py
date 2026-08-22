from typing import Any, Optional, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/applications", tags=["tracking"])


class TrackRequest(BaseModel):
    pass


class TrackResponse(BaseModel):
    success: bool
    normalized_status: Optional[str] = None
    source_status: Optional[str] = None
    message: Optional[str] = None
    reference_number: Optional[str] = None
    status_changed: bool = False
    previous_status: Optional[str] = None
    error: Optional[str] = None


@router.post("/{application_id}/track", response_model=TrackResponse)
async def track_application(application_id: str, user_id: str):
    """Track application status."""
    from apps.api.app.api.applications import _applications_store

    app = _applications_store.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not app.get("reference_number"):
        raise HTTPException(status_code=400, detail="Application has not been submitted yet")

    from packages.applications.tracking_service import ApplicationTrackingService
    from packages.services.adapters.income_certificate.adapter import MockIncomeCertificateAdapter

    tracking_service = ApplicationTrackingService()

    class MockTrackingAdapter:
        async def track(self, reference_number: str) -> Dict[str, Any]:
            adapter = MockIncomeCertificateAdapter()
            result = await adapter.track_application(reference_number)
            return result.data if result.success else {}

        def normalize_status(self, source_status: str) -> str:
            mapping = {
                "submitted": "submitted",
                "under_review": "processing",
                "processing": "processing",
                "under scrutiny": "processing",
                "returned": "action_required",
                "returned for correction": "action_required",
                "issued": "completed",
                "approved": "completed",
            }
            return mapping.get(source_status.lower().strip(), "processing")

    tracking_service.register_adapter(app["service_id"], MockTrackingAdapter())
    result = await tracking_service.track_application(app)

    if result.get("success") and result.get("status_changed"):
        app["status"] = result["normalized_status"]
        _applications_store[application_id] = app

    return TrackResponse(
        success=result.get("success", False),
        normalized_status=result.get("normalized_status"),
        source_status=result.get("source_status"),
        message=result.get("message"),
        reference_number=result.get("reference_number"),
        status_changed=result.get("status_changed", False),
        previous_status=result.get("previous_status"),
        error=result.get("error"),
    )
