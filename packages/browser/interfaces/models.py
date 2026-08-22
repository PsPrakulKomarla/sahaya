from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BrowserActionType(str, Enum):
    NAVIGATE = "NAVIGATE"
    CLICK = "CLICK"
    TYPE = "TYPE"
    SELECT = "SELECT"
    UPLOAD = "UPLOAD"
    EXTRACT_TEXT = "EXTRACT_TEXT"
    EXTRACT_DATA = "EXTRACT_DATA"
    WAIT = "WAIT"
    SCROLL = "SCROLL"
    SCREENSHOT = "SCREENSHOT"
    GO_BACK = "GO_BACK"
    IS_VISIBLE = "IS_VISIBLE"
    GET_PAGE_TITLE = "GET_PAGE_TITLE"
    FIND_ELEMENT = "FIND_ELEMENT"


class ElementTarget(BaseModel):
    description: str = ""
    selector: Optional[str] = None
    text: Optional[str] = None
    role: Optional[str] = None
    aria_label: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)


class BrowserAction(BaseModel):
    type: BrowserActionType
    target: Optional[ElementTarget] = None
    value: Optional[str] = None
    url: Optional[str] = None
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BrowserActionResult(BaseModel):
    success: bool
    action: str
    target: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PageInfo(BaseModel):
    url: str
    title: str
    content: str = ""
    elements: List[Dict[str, Any]] = Field(default_factory=list)
