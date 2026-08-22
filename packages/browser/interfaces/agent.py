from abc import ABC, abstractmethod
from typing import Optional, List
from packages.browser.interfaces.models import (
    BrowserAction,
    BrowserActionResult,
    PageInfo,
)


class BrowserAgent(ABC):
    """Abstract interface for browser automation.

    Implementations must not expose provider-specific APIs.
    """

    @abstractmethod
    async def open(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def navigate(self, url: str) -> BrowserActionResult:
        pass

    @abstractmethod
    async def current_url(self) -> str:
        pass

    @abstractmethod
    async def inspect(self) -> PageInfo:
        pass

    @abstractmethod
    async def execute_action(self, action: BrowserAction) -> BrowserActionResult:
        pass

    @abstractmethod
    async def screenshot(self) -> bytes:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass
