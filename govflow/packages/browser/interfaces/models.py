"""Normalized page model and semantic element representation.

These models provide a browser-provider-agnostic representation of web pages.
All browser adapters must convert their raw output into these models.
The rest of the system consumes PageModel rather than provider-specific output.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ElementType(str, Enum):
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FORM = "form"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    IMAGE = "image"
    TABLE = "table"
    LIST = "list"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    DIV = "div"
    SPAN = "span"
    UNKNOWN = "unknown"


class BrowserActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    UPLOAD = "upload"
    EXTRACT = "extract"
    WAIT = "wait"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    GO_BACK = "go_back"
    HOVER = "hover"
    CHECK = "check"
    UNCHECK = "uncheck"
    KEYS = "keys"


class BrowserEventType(str, Enum):
    BROWSER_STARTED = "browser_started"
    PAGE_LOADED = "page_loaded"
    PAGE_INSPECTED = "page_inspected"
    ELEMENT_FOUND = "element_found"
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    RECOVERY_STARTED = "recovery_started"
    RECOVERY_COMPLETED = "recovery_completed"
    WORKFLOW_LOADED = "workflow_loaded"
    WORKFLOW_CREATED = "workflow_created"
    WORKFLOW_UPDATED = "workflow_updated"
    WORKFLOW_INVALIDATED = "workflow_invalidated"


class SemanticElement(BaseModel):
    """A semantically described page element.

    Elements are identified by role, text, and description rather than
    relying solely on CSS/XPath selectors. Selectors are retained as hints
    but must NOT be the only source of truth.
    """

    element_id: Optional[str] = None
    role: ElementType = ElementType.UNKNOWN
    text: str = ""
    label: str = ""
    description: str = ""
    visible: bool = True
    enabled: bool = True
    selector_hint: Optional[str] = None
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    input_type: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    href: Optional[str] = None
    confidence: float = 1.0
    attributes: Dict[str, Any] = Field(default_factory=dict)

    def semantic_signature(self) -> str:
        """Generate a semantic signature for matching.

        This captures the intent of an element independent of selectors.
        """
        parts = [self.role.value]
        if self.text:
            parts.append(f"text={self.text.lower().strip()}")
        if self.label:
            parts.append(f"label={self.label.lower().strip()}")
        if self.aria_label:
            parts.append(f"aria={self.aria_label.lower().strip()}")
        if self.description:
            parts.append(f"desc={self.description.lower().strip()}")
        return "|".join(parts)


class PageModel(BaseModel):
    """Normalized representation of a web page.

    Browser adapters convert their raw output into this model.
    The rest of the system consumes PageModel rather than raw browser output.
    """

    url: str = ""
    title: str = ""
    text: str = ""
    elements: List[SemanticElement] = Field(default_factory=list)
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    screenshot_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def find_elements(
        self,
        role: Optional[ElementType] = None,
        text: Optional[str] = None,
        visible_only: bool = True,
    ) -> List[SemanticElement]:
        """Find elements matching criteria."""
        results = self.elements
        if visible_only:
            results = [e for e in results if e.visible]
        if role is not None:
            results = [e for e in results if e.role == role]
        if text is not None:
            text_lower = text.lower().strip()
            results = [
                e for e in results
                if text_lower in e.text.lower() or text_lower in e.label.lower()
            ]
        return results

    def find_element(
        self,
        role: Optional[ElementType] = None,
        text: Optional[str] = None,
        visible_only: bool = True,
    ) -> Optional[SemanticElement]:
        """Find a single element matching criteria."""
        elements = self.find_elements(role=role, text=text, visible_only=visible_only)
        return elements[0] if elements else None

    def has_element(self, role: Optional[ElementType] = None, text: Optional[str] = None) -> bool:
        """Check if an element exists on the page."""
        return self.find_element(role=role, text=text) is not None


class BrowserEvent(BaseModel):
    """Normalized browser event for audit and observability."""

    event_type: BrowserEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    url: Optional[str] = None
    element_text: Optional[str] = None
    action: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
