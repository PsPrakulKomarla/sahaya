"""Port (interface) definitions for the grievance engine.

The grievance engine stays independent of the persistence layer and the
government-service adapter layer by depending on these abstract ports.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from packages.grievances.models import Grievance


class GrievanceRepositoryPort(ABC):
    """Persistence port for grievances."""

    @abstractmethod
    async def save(self, grievance: Grievance) -> Grievance:
        pass

    @abstractmethod
    async def get(self, grievance_id: UUID) -> Grievance | None:
        pass

    @abstractmethod
    async def find_by_user(self, user_id: UUID) -> list[Grievance]:
        pass

    @abstractmethod
    async def find_by_application(self, application_id: UUID) -> list[Grievance]:
        pass

    @abstractmethod
    async def delete(self, grievance_id: UUID) -> bool:
        pass


class ApprovalPort(ABC):
    """Port for requesting and recording human approvals."""

    @abstractmethod
    async def request_approval(
        self,
        user_id: UUID,
        action_type: str,
        summary: str,
        metadata: dict[str, Any],
    ) -> str:
        pass

    @abstractmethod
    async def is_approved(self, approval_id: str) -> bool:
        pass

    @abstractmethod
    async def validate_approval(self, approval_id: str) -> bool:
        pass


class ServiceAdapterPort(Protocol):
    """Minimal interface the grievance engine uses from a service adapter."""

    def metadata(self) -> Any:
        pass

    def track_application(self, reference: str) -> Any:
        pass


class GrievanceTrackingAdapter(ABC):
    """Adapter for interacting with a government grievance portal.

    Mock in tests; real implementation will be added in a later phase.
    """

    @abstractmethod
    def track(self, reference_number: str) -> dict[str, Any]:
        """Return ``source_status``/normalized status dict from the portal."""
        pass