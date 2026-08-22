"""Language Service — detection, normalization, and translation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from packages.services.intent.language import LanguageDetector, RuleBasedLanguageDetector
from packages.services.intent.models import Intent, IntentContext, Language


@dataclass
class TranslationResult:
    text: str
    source_language: Language
    target_language: Language
    confidence: float


class TranslationProvider(ABC):
    """Abstract interface for translation providers."""

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
    ) -> TranslationResult: ...

    @abstractmethod
    def supported_languages(self) -> list[Language]: ...


class RuleBasedTranslationProvider(TranslationProvider):
    """Simple rule-based translation for testing/common phrases."""

    _COMMON_PHRASES: dict[str, dict[Language, str]] = {
        "application_pending": {
            Language.ENGLISH: "My application is pending.",
            Language.KANNADA: "ನನ್ನ ಅರ್ಜಿ ಬಾಕಿದಲ್ಲಿದೆ.",
            Language.HINDI: "मेरा आवेदन लंबित है।",
        },
        "application_rejected": {
            Language.ENGLISH: "My application was rejected.",
            Language.KANNADA: "ನನ್ನ ಅರ್ಜಿ ನಿರಾಕರಿಸಲಾಗಿದೆ.",
            Language.HINDI: "मेरा आवेदन अस्वीकार कर दिया गया।",
        },
        "delay_complaint": {
            Language.ENGLISH: "My income certificate application has been pending for two months.",
            Language.KANNADA: "ನನ್ನ ಆದಾಯ ಹಣದ ದಾಖಲೆ ಅರ್ಜಿ ಎರಡು ತಿಂಗಳುಳ ಮೇಲೆ ಬಾಕಿದಲ್ಲಿದೆ.",
            Language.HINDI: "मेरा आय प्रमाण पत्र आवेदन दो महीने से लंबित है।",
        },
    }

    async def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
    ) -> TranslationResult:
        lowered = text.lower().strip()
        for key, translations in self._COMMON_PHRASES.items():
            if lowered in [t.lower() for t in translations.values()]:
                return TranslationResult(
                    text=translations.get(target_language, text),
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.8,
                )
        return TranslationResult(
            text=text,
            source_language=source_language,
            target_language=target_language,
            confidence=0.0,
        )

    def supported_languages(self) -> list[Language]:
        return [Language.ENGLISH, Language.KANNADA, Language.HINDI]


class LLMTranslationProvider(TranslationProvider):
    """LLM-based translation provider (stub for future implementation)."""

    def __init__(self, llm_provider: Any) -> None:
        self._llm = llm_provider

    async def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
    ) -> TranslationResult:
        return TranslationResult(
            text=text,
            source_language=source_language,
            target_language=target_language,
            confidence=0.0,
        )

    def supported_languages(self) -> list[Language]:
        return [Language.ENGLISH, Language.KANNADA, Language.HINDI]


class LanguageService:
    """Orchestrates language detection, normalization, and translation."""

    def __init__(
        self,
        detector: LanguageDetector | None = None,
        translation_provider: TranslationProvider | None = None,
    ) -> None:
        self._detector = detector or RuleBasedLanguageDetector()
        self._translator = translation_provider or RuleBasedTranslationProvider()

    def detect(self, message: str) -> tuple[Language, float]:
        """Detect the language of a message."""
        return self._detector.detect(message)

    async def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
    ) -> TranslationResult:
        """Translate text between languages."""
        return await self._translator.translate(text, source_language, target_language)

    async def normalize_to_internal(
        self,
        message: str,
        context: IntentContext | None = None,
    ) -> tuple[Intent, Language]:
        """Convert user message to language-independent internal representation."""
        detected_lang, confidence = self.detect(message)
        effective_lang = context.language if context and context.language else detected_lang

        normalized = self._normalize_message(message, effective_lang)

        return normalized, effective_lang

    def _normalize_message(self, message: str, language: Language) -> Intent:
        """Normalize message to internal representation (delegates to intent engine)."""
        from packages.services.intent.engine import RuleBasedIntentEngine

        engine = RuleBasedIntentEngine(language_detector=self._detector)
        return engine.parse(message)

    def get_localized_label(
        self,
        key: str,
        language: Language,
        **kwargs: Any,
    ) -> str:
        """Get localized string for a template key."""
        templates: dict[str, dict[Language, str]] = {
            "grievance_created": {
                Language.ENGLISH: "Grievance created successfully.",
                Language.KANNADA: "ಖಾಸಗಿ ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ.",
                Language.HINDI: "शिकायत सफलतापूर्वक बनाई गई।",
            },
            "approval_required": {
                Language.ENGLISH: "Your approval is required to submit this grievance.",
                Language.KANNADA: "ಈ ಖಾಸಗಿ ಸಲ್ಲಿಸಲು ನಿಮ್ಮ ಅನುಮತಿ ಅಗತ್ಯವಿದೆ.",
                Language.HINDI: "इस शिकायत को जमा करने के लिए आपकी अनुमति आवश्यक है।",
            },
            "approval_granted": {
                Language.ENGLISH: "Approval granted. Submitting grievance...",
                Language.KANNADA: "ಅನುಮತಿ ನೀಡಲಾಗಿದೆ. ಖಾಸಗಿ ಸಲ್ಲಿಸಲಾಗುತ್ತಿದೆ...",
                Language.HINDI: "अनुमति प्रदान की गई। शिकायत जमा की जा रही है...",
            },
            "grievance_submitted": {
                Language.ENGLISH: "Grievance submitted with reference {ref}.",
                Language.KANNADA: "ಖಾಸಗಿ {ref} ರೆಫರೆನ್ಸ್‌ 인도 प्रदान ಮಾಡಲಾಗಿದೆ.",
                Language.HINDI: "शिकायत {ref} रेफरेंस के साथ जमा की गई।",
            },
        }
        template = templates.get(key, {}).get(language, key)
        return template.format(**kwargs)

    @property
    def supported_languages(self) -> list[Language]:
        return [Language.ENGLISH, Language.KANNADA, Language.HINDI]