"""Structured output schemas for LLM interactions."""
from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field
from uuid import UUID


class IntentType(StrEnum):
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


class Language(StrEnum):
    ENGLISH = "en"
    KANNADA = "kn"
    HINDI = "hi"


class Jurisdiction(BaseModel):
    country: str | None = None
    state: str | None = None
    district: str | None = None


class IntentOutput(BaseModel):
    """Structured intent output from LLM."""
    intent: IntentType
    service_query: str
    operation: IntentType
    jurisdiction: Jurisdiction = Field(default_factory=Jurisdiction)
    language: Language = Language.ENGLISH
    entities: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    clarification_required: bool = False
    clarification_questions: list[str] = Field(default_factory=list)


class ClarificationOutput(BaseModel):
    """Structured clarification questions from LLM."""
    questions: list[str] = Field(min_length=1, max_length=5)
    context_summary: str


class ServiceExplanation(BaseModel):
    """Structured service explanation from LLM."""
    service_name: str
    description: str
    eligibility_summary: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    processing_time: str | None = None
    fees: str | None = None
    next_steps: list[str] = Field(default_factory=list)


class GrievanceDraftOutput(BaseModel):
    """Structured grievance draft from LLM."""
    subject: str
    description: str
    category: str
    facts: list[dict[str, Any]] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)


class AgentPlanSuggestion(BaseModel):
    """Structured plan suggestion from LLM."""
    steps: list[dict[str, Any]] = Field(default_factory=list)
    estimated_duration_minutes: int | None = None
    requires_human_approval: bool = False
    approval_summary: str | None = None


class ResponseOutput(BaseModel):
    """Structured user-facing response from LLM."""
    message: str
    language: Language
    action_required: bool = False
    suggested_actions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class SafetyCheckOutput(BaseModel):
    """Structured safety check result from LLM."""
    safe: bool
    risk_level: Literal["low", "medium", "high", "critical"]
    concerns: list[str] = Field(default_factory=list)
    recommended_action: Literal["allow", "require_approval", "deny", "ask_user"] = "allow"


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMRequest(BaseModel):
    messages: list[LLMMessage]
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int | None = None
    response_format: type[BaseModel] | None = None


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: dict[str, int] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)