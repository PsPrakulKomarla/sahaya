from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from packages.services.intent import (
    LanguageService,
    RuleBasedLanguageDetector,
    RuleBasedTranslationProvider,
    TranslationResult,
    Language,
)

router = APIRouter(prefix="/language", tags=["language"])

_language_service: Optional[LanguageService] = None


def get_language_service() -> LanguageService:
    global _language_service
    if _language_service is None:
        _language_service = LanguageService(
            detector=RuleBasedLanguageDetector(),
            translation_provider=RuleBasedTranslationProvider(),
        )
    return _language_service


class LanguageDetectRequest(BaseModel):
    message: str = Field(..., description="Text to detect language for")


class LanguageDetectResponse(BaseModel):
    language: str
    confidence: float


class LanguageTranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(..., description="Source language code (en, kn, hi)")
    target_language: str = Field(..., description="Target language code (en, kn, hi)")


class LanguageTranslateResponse(BaseModel):
    text: str
    source_language: str
    target_language: str
    confidence: float


class LocalizeRequest(BaseModel):
    key: str = Field(..., description="Template key")
    language: str = Field(..., description="Target language code")
    params: dict = Field(default_factory=dict, description="Template parameters")


class LocalizeResponse(BaseModel):
    text: str


@router.post("/detect", response_model=LanguageDetectResponse)
async def detect_language(
    request: LanguageDetectRequest,
    service: LanguageService = Depends(get_language_service),
):
    """Detect the language of a message."""
    lang, confidence = service.detect(request.message)
    return LanguageDetectResponse(language=lang.value, confidence=confidence)


@router.post("/translate", response_model=LanguageTranslateResponse)
async def translate_text(
    request: LanguageTranslateRequest,
    service: LanguageService = Depends(get_language_service),
):
    """Translate text between languages."""
    try:
        source_lang = Language(request.source_language)
        target_lang = Language(request.target_language)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid language code")

    result: TranslationResult = await service.translate(
        request.text, source_lang, target_lang
    )
    return LanguageTranslateResponse(
        text=result.text,
        source_language=result.source_language.value,
        target_language=result.target_language.value,
        confidence=result.confidence,
    )


@router.post("/localize", response_model=LocalizeResponse)
async def localize_text(
    request: LocalizeRequest,
    service: LanguageService = Depends(get_language_service),
):
    """Get localized string for a template key."""
    try:
        lang = Language(request.language)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid language code")

    text = service.get_localized_label(request.key, lang, **request.params)
    return LocalizeResponse(text=text)