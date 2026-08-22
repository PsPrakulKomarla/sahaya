from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from packages.ai import (
    LLMClient,
    MockLLMProvider,
    LLMSafetyValidator,
    IntentOutput,
    Language,
)
from packages.services.intent import RuleBasedLanguageDetector, RuleBasedIntentEngine
from packages.services.registry import ServiceResolver

router = APIRouter(prefix="/ai", tags=["ai"])

_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        provider = MockLLMProvider()
        safety = LLMSafetyValidator()
        _llm_client = LLMClient(provider=provider, safety_validator=safety)
    return _llm_client


class AIUnderstandRequest(BaseModel):
    message: str = Field(..., description="User's natural language message")
    language: Optional[str] = Field(None, description="Language code (en, kn, hi)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Conversation context")


class LanguageInfo(BaseModel):
    detected: str
    confidence: float


class IntentInfo(BaseModel):
    intent: str
    service_query: str
    operation: str
    jurisdiction: Dict[str, Optional[str]]
    language: str
    entities: Dict[str, Any]
    confidence: float
    clarification_required: bool
    clarification_questions: list[str]


class ServiceResolutionInfo(BaseModel):
    status: str
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    operation: Optional[str] = None
    jurisdiction: Optional[Dict[str, Optional[str]]] = None
    capabilities: list[str] = []
    workflow_version: Optional[str] = None
    confidence: float = 0.0
    clarification_questions: list[str] = []
    reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AIUnderstandResponse(BaseModel):
    language: LanguageInfo
    intent: IntentInfo
    service_resolution: ServiceResolutionInfo
    clarification: Optional[list[str]] = None


@router.post("/understand", response_model=AIUnderstandResponse)
async def understand_message(
    request: AIUnderstandRequest,
    client: LLMClient = Depends(get_llm_client),
):
    """Understand a message: detect language, parse intent, resolve service."""
    detector = RuleBasedLanguageDetector()

    if request.language:
        try:
            detected_lang = Language(request.language)
            confidence = 1.0
        except ValueError:
            detected_lang, confidence = detector.detect(request.message)
    else:
        detected_lang, confidence = detector.detect(request.message)

    engine = RuleBasedIntentEngine(language_detector=detector)
    intent_ctx = None
    if request.context:
        from packages.services.intent import IntentContext
        intent_ctx = IntentContext(
            language=detected_lang,
            country=request.context.get("country"),
            state=request.context.get("state"),
            district=request.context.get("district"),
            previous_service=request.context.get("previous_service"),
            previous_task=request.context.get("previous_task"),
            conversation_context=request.context,
        )

    intent = engine.parse(request.message, intent_ctx)

    resolver = ServiceResolver()
    resolution = await resolver.resolve_intent(intent)

    clarification = None
    if intent.clarification_required:
        clarification = intent.clarification_questions

    return AIUnderstandResponse(
        language=LanguageInfo(detected=detected_lang.value, confidence=confidence),
        intent=IntentInfo(
            intent=intent.intent.value,
            service_query=intent.service_query,
            operation=intent.operation.value,
            jurisdiction={
                "country": intent.jurisdiction.country,
                "state": intent.jurisdiction.state,
                "district": intent.jurisdiction.district,
            },
            language=intent.language.value,
            entities=intent.entities,
            confidence=intent.confidence,
            clarification_required=intent.clarification_required,
            clarification_questions=intent.clarification_questions,
        ),
        service_resolution=ServiceResolutionInfo(
            status=resolution.status.value,
            service_id=resolution.service_id,
            service_name=resolution.service_name,
            operation=resolution.operation,
            jurisdiction={
                "country": resolution.jurisdiction.country if resolution.jurisdiction else None,
                "state": resolution.jurisdiction.state if resolution.jurisdiction else None,
                "district": resolution.jurisdiction.district if resolution.jurisdiction else None,
            } if resolution.jurisdiction else None,
            capabilities=resolution.capabilities,
            workflow_version=resolution.workflow_version,
            confidence=resolution.confidence,
            clarification_questions=resolution.clarification_questions,
            reason=resolution.reason,
            metadata=resolution.metadata,
        ),
        clarification=clarification,
    )