from abc import ABC, abstractmethod
from typing import Any


class TrackingAdapter(ABC):
    """Abstract base class for application tracking adapters.

    Each service adapter can implement tracking via this interface.
    """

    @abstractmethod
    async def track(self, reference_number: str) -> dict[str, Any]:
        """Track application status by reference number.

        Returns:
            Dict with keys: status, source_status, message, last_updated,
            reference_number, next_steps, timeline
        """

    @abstractmethod
    def normalize_status(self, source_status: str) -> str:
        """Normalize portal-specific status to standard status."""
