from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from packages.services.intent import (
    IntentEngine,
    RuleBasedIntentEngine,
    Intent,
    IntentContext,
    Language,
)
from packages.services.registry import ServiceResolver, ServiceResolution

router = APIRouter(prefix="/intent", tags=["intent"])

_intent_engine: Optional[IntentEngine] = None


def get_intent_engine() -> IntentEngine:
    global _intent_engine
    if _intent_engine is None:
        _intent_engine = RuleBasedIntentEngine()
    return _intent_engine


def set_intent_engine(engine: IntentEngine) -> None:
    global _intent_engine
    _intent_engine = engine


class IntentContextRequest(BaseModel):
    language: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    previous_service: Optional[str] = None
    previous_task: Optional[str] = None


class IntentParseRequest(BaseModel):
    message: str = Field(..., description="Natural language message from the user")
    context: Optional[IntentContextRequest] = None


class JurisdictionResponse(BaseModel):
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class IntentParseResponse(BaseModel):
    intent: str
    service_query: str
    operation: str
    jurisdiction: JurisdictionResponse
    language: str
    entities: Dict[str, Any]
    confidence: float
    clarification_required: bool
    clarification_questions: List[str]


class ServiceResolveRequest(BaseModel):
    intent: IntentParseResponse


class ServiceResolutionJurisdiction(BaseModel):
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class ServiceResolveResponse(BaseModel):
    status: str
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    operation: Optional[str] = None
    jurisdiction: Optional[ServiceResolutionJurisdiction] = None
    capabilities: List[str] = []
    workflow_version: Optional[str] = None
    confidence: float = 0.0
    clarification_questions: List[str] = []
    reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AgentUnderstandRequest(BaseModel):
    message: str = Field(..., description="Natural language message from the user")
    context: Optional[IntentContextRequest] = None


class AgentUnderstandResponse(BaseModel):
    intent: IntentParseResponse
    resolution: ServiceResolveResponse


@router.post("/parse", response_model=IntentParseResponse)
async def parse_intent(request: IntentParseRequest):
    """Parse a natural language message into a structured intent."""
    engine = get_intent_engine()

    context = None
    if request.context:
        lang = None
        if request.context.language:
            try:
                lang = Language(request.context.language)
            except ValueError:
                pass

        context = IntentContext(
            language=lang,
            country=request.context.country,
            state=request.context.state,
            district=request.context.district,
            previous_service=request.context.previous_service,
            previous_task=request.context.previous_task,
        )

    intent = engine.parse(request.message, context)

    return IntentParseResponse(
        intent=intent.intent,
        service_query=intent.service_query,
        operation=intent.operation,
        jurisdiction=JurisdictionResponse(
            country=intent.jurisdiction.country,
            state=intent.jurisdiction.state,
            district=intent.jurisdiction.district,
        ),
        language=intent.language,
        entities=intent.entities,
        confidence=intent.confidence,
        clarification_required=intent.clarification_required,
        clarification_questions=intent.clarification_questions,
    )


@router.post("/resolve", response_model=ServiceResolveResponse)
async def resolve_service(request: ServiceResolveRequest):
    """Resolve a parsed intent to a specific government service."""
    resolver = ServiceResolver()

    intent = Intent(
        intent=request.intent.intent,
        service_query=request.intent.service_query,
        operation=request.intent.operation,
        jurisdiction={
            "country": request.intent.jurisdiction.country,
            "state": request.intent.jurisdiction.state,
            "district": request.intent.jurisdiction.district,
        },
        language=request.intent.language,
        entities=request.intent.entities,
        confidence=request.intent.confidence,
    )

    resolution = await resolver.resolve_intent(intent)

    return ServiceResolveResponse(
        status=resolution.status,
        service_id=resolution.service_id,
        service_name=resolution.service_name,
        operation=resolution.operation,
        jurisdiction=ServiceResolutionJurisdiction(
            country=resolution.jurisdiction.country if resolution.jurisdiction else None,
            state=resolution.jurisdiction.state if resolution.jurisdiction else None,
            district=resolution.jurisdiction.district if resolution.jurisdiction else None,
        ),
        capabilities=resolution.capabilities,
        workflow_version=resolution.workflow_version,
        confidence=resolution.confidence,
        clarification_questions=resolution.clarification_questions,
        reason=resolution.reason,
        metadata=resolution.metadata,
    )


@router.post("/understand", response_model=AgentUnderstandResponse)
async def understand_message(request: AgentUnderstandRequest):
    """Understand a message: parse intent and resolve service in one step."""
    engine = get_intent_engine()

    context = None
    if request.context:
        lang = None
        if request.context.language:
            try:
                lang = Language(request.context.language)
            except ValueError:
                pass

        context = IntentContext(
            language=lang,
            country=request.context.country,
            state=request.context.state,
            district=request.context.district,
            previous_service=request.context.previous_service,
            previous_task=request.context.previous_task,
        )

    intent = engine.parse(request.message, context)

    intent_response = IntentParseResponse(
        intent=intent.intent,
        service_query=intent.service_query,
        operation=intent.operation,
        jurisdiction=JurisdictionResponse(
            country=intent.jurisdiction.country,
            state=intent.jurisdiction.state,
            district=intent.jurisdiction.district,
        ),
        language=intent.language,
        entities=intent.entities,
        confidence=intent.confidence,
        clarification_required=intent.clarification_required,
        clarification_questions=intent.clarification_questions,
    )

    resolver = ServiceResolver()
    resolution = await resolver.resolve_intent(intent)

    resolution_response = ServiceResolveResponse(
        status=resolution.status,
        service_id=resolution.service_id,
        service_name=resolution.service_name,
        operation=resolution.operation,
        jurisdiction=ServiceResolutionJurisdiction(
            country=resolution.jurisdiction.country if resolution.jurisdiction else None,
            state=resolution.jurisdiction.state if resolution.jurisdiction else None,
            district=resolution.jurisdiction.district if resolution.jurisdiction else None,
        ),
        capabilities=resolution.capabilities,
        workflow_version=resolution.workflow_version,
        confidence=resolution.confidence,
        clarification_questions=resolution.clarification_questions,
        reason=resolution.reason,
        metadata=resolution.metadata,
    )

    return AgentUnderstandResponse(
        intent=intent_response,
        resolution=resolution_response,
    )
