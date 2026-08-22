from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Supported intent types."""
    SERVICE_DISCOVERY = "SERVICE_DISCOVERY"
    ELIGIBILITY_CHECK = "ELIGIBILITY_CHECK"
    DOCUMENT_REQUIREMENTS = "DOCUMENT_REQUIREMENTS"
    NEW_APPLICATION = "NEW_APPLICATION"
    UPDATE_RECORD = "UPDATE_RECORD"
    RENEWAL = "RENEWAL"
    TRACK_APPLICATION = "TRACK_APPLICATION"
    RAISE_GRIEVANCE = "RAISE_GRIEVANCE"
    GENERAL_SERVICE_INFORMATION = "GENERAL_SERVICE_INFORMATION"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    KANNADA = "kn"
    HINDI = "hi"


class Jurisdiction(BaseModel):
    """Jurisdiction context for intent resolution."""
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class IntentContext(BaseModel):
    """Context for intent parsing."""
    language: Optional[Language] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    previous_service: Optional[str] = None
    previous_task: Optional[str] = None
    conversation_context: Optional[Dict[str, Any]] = None


class Intent(BaseModel):
    """Structured intent parsed from user message."""
    intent: IntentType
    service_query: str
    operation: IntentType
    jurisdiction: Jurisdiction = Field(default_factory=Jurisdiction)
    language: Language = Language.ENGLISH
    entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    clarification_required: bool = False
    clarification_questions: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True
