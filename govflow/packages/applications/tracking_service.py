from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger

from packages.applications.application_service import STATUS_NORMALIZATION
from packages.applications.tracking_adapter import TrackingAdapter

logger = get_logger(__name__)


class ApplicationTrackingService:
    """Tracks application status across government portals."""

    def __init__(self):
        self._adapters: dict[str, TrackingAdapter] = {}

    def register_adapter(self, service_id: str, adapter: TrackingAdapter) -> None:
        self._adapters[service_id] = adapter
        logger.info("tracking_adapter_registered", service_id=service_id)

    def get_adapter(self, service_id: str) -> TrackingAdapter | None:
        return self._adapters.get(service_id)

    async def track_application(
        self,
        application: dict[str, Any],
    ) -> dict[str, Any]:
        service_id = application.get("service_id", "")
        reference_number = application.get("reference_number", "")

        if not reference_number:
            return {
                "success": False,
                "error": "No reference number available for tracking",
            }

        adapter = self._adapters.get(service_id)
        if not adapter:
            return {
                "success": False,
                "error": f"No tracking adapter registered for service '{service_id}'",
            }

        try:
            raw_result = await adapter.track(reference_number)
            normalized_status = adapter.normalize_status(raw_result.get("status", ""))

            previous_status = application.get("status")
            status_changed = previous_status != normalized_status

            timeline_events: list[dict[str, Any]] = []
            if status_changed:
                event = {
                    "event_type": "STATUS_CHANGED",
                    "status": normalized_status,
                    "note": f"Status changed from {previous_status} to {normalized_status}",
                    "source_status": raw_result.get("status", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                timeline_events.append(event)
                logger.info(
                    "status_changed",
                    application_id=application.get("id"),
                    previous=previous_status,
                    current=normalized_status,
                )

            return {
                "success": True,
                "normalized_status": normalized_status,
                "source_status": raw_result.get("status", ""),
                "message": raw_result.get("message", ""),
                "last_updated": raw_result.get("last_updated", datetime.now(timezone.utc).isoformat()),
                "reference_number": reference_number,
                "next_steps": raw_result.get("next_steps", []),
                "timeline": raw_result.get("timeline", []),
                "status_changed": status_changed,
                "previous_status": previous_status,
                "timeline_events": timeline_events,
            }

        except (RuntimeError, ValueError, KeyError, TypeError, ConnectionError) as e:
            logger.error("tracking_error", application_id=application.get("id"), error=str(e))
            return {"success": False, "error": str(e)}

    def normalize_status(self, source_status: str) -> str:
        normalized = STATUS_NORMALIZATION.get(source_status.lower().strip(), "processing")
        return normalized

    def create_tracking_job(
        self,
        application_id: str,
        service_id: str,
        reference_number: str,
        interval_seconds: int = 3600,
    ) -> dict[str, Any]:
        return {
            "job_id": f"track_{application_id}",
            "application_id": application_id,
            "service_id": service_id,
            "reference_number": reference_number,
            "interval_seconds": interval_seconds,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
