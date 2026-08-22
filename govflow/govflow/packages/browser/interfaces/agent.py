"""BrowserAgent abstract interface.

All browser providers (webcmd, Playwright, future providers) must implement
this interface. The rest of the system depends only on this abstraction.

The interface is intentionally provider-agnostic. It describes browser
operations in terms of page models and semantic elements, not CSS selectors
or provider-specific APIs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from packages.browser.interfaces.models import (
    BrowserActionType,
    BrowserEvent,
    PageModel,
    SemanticElement,
)


class BrowserConfig(BaseModel):
    """Configuration for browser agents."""

    headless: bool = True
    timeout_seconds: int = 60
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class BrowserResult(BaseModel):
    """Result of a browser operation."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    page: Optional[PageModel] = None
    events: List[BrowserEvent] = Field(default_factory=list)


class BrowserAgent(ABC):
    """Abstract browser agent interface.

    All browser providers must implement this interface. The interface
    operates on normalized PageModel and SemanticElement objects rather
    than provider-specific representations.
    """

    @abstractmethod
    async def open(self, config: Optional[BrowserConfig] = None) -> BrowserResult:
        """Open a browser instance."""
        pass

    @abstractmethod
    async def close(self) -> BrowserResult:
        """Close the browser and clean up resources."""
        pass

    @abstractmethod
    async def navigate(self, url: str) -> BrowserResult:
        """Navigate to a URL and return the loaded page."""
        pass

    @abstractmethod
    async def current_url(self) -> str:
        """Return the current URL."""
        pass

    @abstractmethod
    async def inspect(self) -> PageModel:
        """Inspect the current page and return a normalized PageModel."""
        pass

    @abstractmethod
    async def find_element(
        self,
        role: Optional[str] = None,
        text: Optional[str] = None,
        selector: Optional[str] = None,
    ) -> Optional[SemanticElement]:
        """Find a single element on the page."""
        pass

    @abstractmethod
    async def click(self, target: str, selector: Optional[str] = None) -> BrowserResult:
        """Click an element identified by text or selector."""
        pass

    @abstractmethod
    async def type_text(
        self, target: str, text: str, selector: Optional[str] = None
    ) -> BrowserResult:
        """Type text into an input field."""
        pass

    @abstractmethod
    async def select(
        self, target: str, value: str, selector: Optional[str] = None
    ) -> BrowserResult:
        """Select an option from a dropdown."""
        pass

    @abstractmethod
    async def upload(
        self, target: str, file_path: str, selector: Optional[str] = None
    ) -> BrowserResult:
        """Upload a file to a file input."""
        pass

    @abstractmethod
    async def extract_text(self) -> str:
        """Extract all visible text from the current page."""
        pass

    @abstractmethod
    async def extract_structured_data(self) -> Dict[str, Any]:
        """Extract structured data from the current page."""
        pass

    @abstractmethod
    async def wait(self, seconds: float) -> BrowserResult:
        """Wait for a specified duration."""
        pass

    @abstractmethod
    async def screenshot(self, path: Optional[str] = None) -> BrowserResult:
        """Take a screenshot of the current page."""
        pass

    @abstractmethod
    async def go_back(self) -> BrowserResult:
        """Navigate back in browser history."""
        pass

    @abstractmethod
    async def scroll(self, direction: str = "down", amount: int = 3) -> BrowserResult:
        """Scroll the page."""
        pass

    @abstractmethod
    async def is_visible(self, target: str, selector: Optional[str] = None) -> bool:
        """Check if an element is visible on the page."""
        pass

    @abstractmethod
    async def get_page_title(self) -> str:
        """Get the current page title."""
        pass

    async def __aenter__(self) -> "BrowserAgent":
        await self.open()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
