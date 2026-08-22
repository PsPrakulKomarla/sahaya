from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ResolutionStatus(str, Enum):
    """Status of service resolution."""
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    JURISDICTION_REQUIRED = "JURISDICTION_REQUIRED"
    CAPABILITY_UNSUPPORTED = "CAPABILITY_UNSUPPORTED"
    SERVICE_DISABLED = "SERVICE_DISABLED"
    WORKFLOW_UNAVAILABLE = "WORKFLOW_UNAVAILABLE"
    INVALID_REQUEST = "INVALID_REQUEST"


class ResolutionJurisdiction(BaseModel):
    """Jurisdiction information in resolution result."""
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class ServiceResolution(BaseModel):
    """Result of service resolution."""
    status: ResolutionStatus
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    operation: Optional[str] = None
    jurisdiction: Optional[ResolutionJurisdiction] = None
    capabilities: List[str] = Field(default_factory=list)
    workflow_version: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    clarification_questions: List[str] = Field(default_factory=list)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class ResolutionError(BaseModel):
    """Structured error for resolution failures."""
    code: str
    message: str
    recoverable: bool = True
    suggested_action: Optional[str] = None
