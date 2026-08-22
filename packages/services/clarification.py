"""Clarification Engine — generates minimal, relevant questions."""
from __future__ import annotations

from typing import Any

from packages.ai.schemas import ClarificationOutput
from packages.ai.client import LLMClient
from packages.services.intent.models import Intent, IntentType


class ClarificationEngine:
    """Generates concise clarification questions when information is missing."""

    # Pre-defined clarification patterns for common scenarios
    PATTERNS: dict[IntentType, list[str]] = {
        IntentType.NEW_APPLICATION: [
            "Which government service do you want to apply for?",
            "What is your state/jurisdiction?",
        ],
        IntentType.TRACK_APPLICATION: [
            "What is your application reference number?",
            "Which service was the application for?",
        ],
        IntentType.RAISE_GRIEVANCE: [
            "Which application or service is this grievance about?",
            "What type of issue are you experiencing?",
        ],
        IntentType.ELIGIBILITY_CHECK: [
            "Which service do you want to check eligibility for?",
            "What is your state/jurisdiction?",
        ],
        IntentType.DOCUMENT_REQUIREMENTS: [
            "Which service do you need documents for?",
            "What is your state/jurisdiction?",
        ],
        IntentType.RENEWAL: [
            "Which license or certificate do you want to renew?",
            "What is the expiry date?",
        ],
        IntentType.UPDATE_RECORD: [
            "Which record do you want to update?",
            "What information needs to be changed?",
        ],
        IntentType.SERVICE_DISCOVERY: [
            "What type of service are you looking for?",
            "What is your location (state/district)?",
        ],
        IntentType.GENERAL_SERVICE_INFORMATION: [
            "Which service would you like information about?",
        ],
    }

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client

    def generate(
        self,
        intent: IntentType,
        missing_fields: list[str] | None = None,
        context: dict[str, Any] | None = None,
        language: str = "en",
    ) -> list[str]:
        """Generate clarification questions using patterns or LLM."""
        questions = self.PATTERNS.get(intent, [])

        if missing_fields:
            for field in missing_fields:
                if field.lower() not in " ".join(questions).lower():
                    questions.append(f"What is your {field.replace('_', ' ')}?")

        if not questions:
            questions = ["Could you please provide more details?"]

        if language != "en":
            questions = self._localize_questions(questions, language)

        return questions[:3]

    async def generate_with_llm(
        self,
        message: str,
        missing_fields: list[str] | None = None,
        context: dict[str, Any] | None = None,
        language: str = "en",
    ) -> list[str]:
        """Generate clarification questions using LLM."""
        if not self._llm:
            return self.generate(
                IntentType.CLARIFICATION_REQUIRED,
                missing_fields,
                context,
                language,
            )

        result: ClarificationOutput = await self._llm.generate_clarification(
            message=message,
            missing_info=missing_fields or [],
            context=context,
        )

        questions = result.questions
        if language != "en":
            questions = self._localize_questions(questions, language)

        return questions[:3]

    def _localize_questions(self, questions: list[str], language: str) -> list[str]:
        """Localize questions to target language."""
        translations = {
            "Which government service do you want to apply for?": {
                "kn": "ನೀವು ಯಾವ ಸರ್ಕಾರ ಸೇವೆಗೆ ಅರ್ಜಿ ಮಾಡಲು ಇಚ್ಛಿಸುತ್ತೀರಿ?",
                "hi": "आप किस सरकारी सेवा के लिए आवेदन करना चाहते हैं?",
            },
            "What is your state/jurisdiction?": {
                "kn": "ನಿಮ್ಮ ರಾಜ್ಯ/ಅಧಿಕಾರ extranjeros ನಿಮ್ಮ ರಿಯಾ?",
                "hi": "आपका राज्य/क्षेत्राधिकार क्या है?",
            },
            "What is your application reference number?": {
                "kn": "ನಿಮ್ಮ ಅರ್ಜಿ রেফರೆನ್ಸ್ ಸಂಖ್ಯೆ ಏನು?",
                "hi": "आपका आवेदन संदर्भ संख्या क्या है?",
            },
            "Which service was the application for?": {
                "kn": "ಅರ್ಜಿ ಯಾವ ಸೇವೆಗಾಗಿತ್ತು?",
                "hi": "आवेदन किस सेवा के लिए था?",
            },
            "Which application or service is this grievance about?": {
                "kn": "ಈ ಖಾಸಗಿ ಯಾವ ಅರ್ಜಿ ಅಥವಾ ಸೇವೆ ಬಗ್ಗೆ?",
                "hi": "यह शिकायत किस आवेदन या सेवा के बारे में है?",
            },
            "What type of issue are you experiencing?": {
                "kn": "ನೀವು ಯಾವ ರೀತಿಯ ಸಮಸ್ಯೆಯನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ?",
                "hi": "आप किस प्रकार की समस्या का सामना कर रहे हैं?",
            },
            "Could you please provide more details?": {
                "kn": "ದಯವಿಟ್ಟು ಹೆಚ್ಚಿನ ವಿವರಗಳನ್ನು ಒದಗಿಸಬಹುದೇ?",
                "hi": "कृपया अधिक विवरण प्रदान करें?",
            },
        }

        localized = []
        for q in questions:
            trans = translations.get(q, {})
            localized.append(trans.get(language, q))
        return localized