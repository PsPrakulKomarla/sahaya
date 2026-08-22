"""Status normalization for grievance portals that use arbitrary wording."""
from __future__ import annotations

from collections import OrderedDict

from packages.grievances.models import GrievanceStatus


# Ordered: longest/most-specific match first via substring lookup.
_SOURCE_STATUS_MAP: "OrderedDict[str, GrievanceStatus]" = OrderedDict(
    [
        ("resolved", GrievanceStatus.RESOLVED),
        ("closed", GrievanceStatus.RESOLVED),
        ("disposed", GrievanceStatus.RESOLVED),
        ("dismissed", GrievanceStatus.REJECTED),
        ("rejected", GrievanceStatus.REJECTED),
        ("rejected by", GrievanceStatus.REJECTED),
        ("processing", GrievanceStatus.PROCESSING),
        ("under examination", GrievanceStatus.PROCESSING),
        ("under review", GrievanceStatus.PROCESSING),
        ("with the department", GrievanceStatus.PROCESSING),
        ("forwarded", GrievanceStatus.PROCESSING),
        ("action required", GrievanceStatus.ACTION_REQUIRED),
        ("awaiting response", GrievanceStatus.ACTION_REQUIRED),
        ("awaiting documents", GrievanceStatus.ACTION_REQUIRED),
        ("additional information required", GrievanceStatus.ACTION_REQUIRED),
        ("more information required", GrievanceStatus.ACTION_REQUIRED),
        ("registered", GrievanceStatus.SUBMITTED),
        ("complaint registered", GrievanceStatus.SUBMITTED),
        ("submitted", GrievanceStatus.SUBMITTED),
        ("pending", GrievanceStatus.PROCESSING),
        ("in progress", GrievanceStatus.PROCESSING),
        ("failed", GrievanceStatus.FAILED),
        ("error", GrievanceStatus.FAILED),
    ]
)


def normalize_status(source_status: str | None) -> GrievanceStatus:
    """Normalize an arbitrary portal status string into a ``GrievanceStatus``."""
    if not source_status:
        return GrievanceStatus.DRAFT
    lowered = source_status.lower().strip()
    for needle, status in _SOURCE_STATUS_MAP.items():
        if needle in lowered:
            return status
    # Heuristic fallbacks for common words.
    for word, status in {
        "resolved": GrievanceStatus.RESOLVED,
        "rejected": GrievanceStatus.REJECTED,
        "processing": GrievanceStatus.PROCESSING,
        "submitted": GrievanceStatus.SUBMITTED,
    }.items():
        if word in lowered:
            return status
    return GrievanceStatus.PROCESSING


# Canonical human-readable labels (language-independent keys kept stable).
STATUS_LABELS: dict[GrievanceStatus, str] = {
    GrievanceStatus.DRAFT: "Draft",
    GrievanceStatus.PREPARING: "Preparing",
    GrievanceStatus.READY_FOR_REVIEW: "Ready for review",
    GrievanceStatus.AWAITING_APPROVAL: "Awaiting approval",
    GrievanceStatus.SUBMITTED: "Submitted",
    GrievanceStatus.PROCESSING: "Processing",
    GrievanceStatus.ACTION_REQUIRED: "Action required",
    GrievanceStatus.RESOLVED: "Resolved",
    GrievanceStatus.REJECTED: "Rejected",
    GrievanceStatus.FAILED: "Failed",
    GrievanceStatus.CANCELLED: "Cancelled",
}