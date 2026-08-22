"""Domain-level errors for the grievance engine."""
from __future__ import annotations

from uuid import UUID


class GrievanceError(Exception):
    """Base class for all grievance domain errors."""

    error_code: str = "GRIEVANCE_ERROR"

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code


class GrievanceNotFound(GrievanceError):
    def __init__(self, grievance_id: UUID) -> None:
        super().__init__(
            f"Grievance '{grievance_id}' was not found.",
            error_code="GRIEVANCE_NOT_FOUND",
        )


class GrievanceNotOwned(GrievanceError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(
            f"User '{user_id}' does not own this grievance.",
            error_code="GRIEVANCE_NOT_OWNED",
        )


class InvalidStateTransition(GrievanceError):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            f"Cannot transition grievance from '{current}' to '{target}'.",
            error_code="INVALID_STATE_TRANSITION",
        )


class ApprovalRequired(GrievanceError):
    def __init__(self) -> None:
        super().__init__(
            "This action requires explicit human approval.",
            error_code="APPROVAL_REQUIRED",
        )


class ApprovalInvalidated(GrievanceError):
    def __init__(self) -> None:
        super().__init__(
            "The grievance changed after approval; a new approval is required.",
            error_code="APPROVAL_INVALIDATED",
        )


class CapabilityUnsupportedError(GrievanceError):
    def __init__(self, capability: str, service_id: str) -> None:
        super().__init__(
            f"Capability '{capability}' is not supported by service '{service_id}'.",
            error_code="CAPABILITY_UNSUPPORTED",
        )


class AmbiguousApplication(GrievanceError):
    def __init__(self, application_ids: list[UUID]) -> None:
        super().__init__(
            "Multiple applications match; user clarification is required.",
            error_code="AMBIGUOUS_APPLICATION",
        )
        self.application_ids = application_ids


class GrievanceSubmissionFailed(GrievanceError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            f"Grievance submission failed: {detail}",
            error_code="GRIEVANCE_SUBMISSION_FAILED",
        )
