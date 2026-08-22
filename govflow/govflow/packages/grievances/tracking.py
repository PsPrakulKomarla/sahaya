"""Grievance tracking service with source-status normalization."""
from __future__ import annotations

from typing import Any

from packages.grievances.models import (
    Grievance,
    TrackResult,
    GrievanceStatus,
    utcnow,
)
from packages.grievances.status import normalize_status, STATUS_LABELS
from packages.grievances.ports import GrievanceTrackingAdapter


class GrievanceTrackingService:
    """Tracks a grievance against a government portal (tracked via its adapter)."""

    def __init__(self, adapter: GrievanceTrackingAdapter | None = None) -> None:
        self._adapter = adapter

    def set_adapter(self, adapter: GrievanceTrackingAdapter) -> None:
        self._adapter = adapter

    def track(self, grievance: Grievance) -> TrackResult:
        """Refresh a grievance's status from its source.

        When no submission reference exists yet, the grievance cannot be
        tracked against the external portal; callers are expected to obtain
        the reference through submission.
        """
        if self._adapter is None or not grievance.official_reference_number:
            return TrackResult(
                official_reference_number=grievance.official_reference_number or "",
                source_status="unsubmitted",
                normalized_status=grievance.status,
                status_changed=False,
            )

        raw: dict[str, Any] = self._adapter.track(grievance.official_reference_number)
        source_status = raw.get("source_status", "unknown")
        normalized = normalize_status(source_status)

        status_changed = normalized != grievance.status
        if status_changed:
            grievance.status = normalized
            grievance.source_status = source_status
            grievance.last_checked_at = utcnow()
            grievance.append_event(
                __import__("packages.grievances.models", fromlist=["GrievanceTimelineEvent"]).GrievanceTimelineEvent.STATUS_CHANGED,
                note=f"Status changed to {normalized.value} (source: {source_status}).",
            )
            if normalized == GrievanceStatus.RESOLVED:
                grievance.completed_at = utcnow()
            elif normalized == GrievanceStatus.FAILED:
                grievance.completed_at = utcnow()
        else:
            grievance.last_checked_at = utcnow()

        return TrackResult(
            official_reference_number=grievance.official_reference_number,
            source_status=source_status,
            normalized_status=normalized,
            status_changed=status_changed,
            raw={k: v for k, v in raw.items() if k.lower() not in {"reference_number"}},
        )

    @staticmethod
    def label(status: GrievanceStatus) -> str:
        return STATUS_LABELS.get(status, status.value)