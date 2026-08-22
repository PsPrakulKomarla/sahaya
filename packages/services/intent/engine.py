from abc import ABC, abstractmethod
from typing import Optional
from packages.services.intent.models import Intent, IntentContext
from packages.services.intent.language import LanguageDetector, RuleBasedLanguageDetector


class IntentEngine(ABC):
    """Abstract interface for intent parsing.

    The IntentEngine converts natural language messages into structured intents.
    Implementations should be replaceable without modifying other components.
    """

    @abstractmethod
    def parse(self, message: str, context: Optional[IntentContext] = None) -> Intent:
        """Parse a natural language message into a structured intent.

        Args:
            message: The user's natural language message.
            context: Optional context for intent parsing.

        Returns:
            A structured Intent object.
        """
        pass


class RuleBasedIntentEngine(IntentEngine):
    """Deterministic, rule-based intent engine.

    This implementation uses pattern matching and keyword detection.
    It is suitable for testing and does not require external LLM APIs.
    """

    INTENT_PATTERNS = {
        "NEW_APPLICATION": [
            "apply for",
            "apply to",
            "new application",
            "create application",
            "start application",
            "register for",
            "get a",
            "obtain",
            "need a",
            "want a",
            "want to apply",
            "need to apply",
            "ಅರ್ಜಿ ಸಲ್ಲಿಸ",
            "ಅರ್ಜಿ ಮಾಡ",
            "आवेदन करना",
            "आवेदन करें",
        ],
        "UPDATE_RECORD": [
            "update",
            "change",
            "modify",
            "correct",
            "edit",
            "update my",
            "change my",
            "modify my",
            "correct my",
            "update address",
            "change address",
            "update name",
            "change name",
            "ಬದಲಾಯಿಸ",
            "ನವೀಕರಿಸ",
            "अपडेट करना",
            "बदलना",
        ],
        "RENEWAL": [
            "renew",
            "renewal",
            "renew my",
            "extend",
            "extension",
            "renew license",
            "renew certificate",
            "ನವೀಕರಿಸ",
            "पुनर्नवीकरण",
        ],
        "TRACK_APPLICATION": [
            "track",
            "check status",
            "status of",
            "where is my",
            "what is the status",
            "track my",
            "check my application",
            "track application",
            "ಹಾಡುವುದು",
            "ಸ್ಥಿತಿ",
            "ट्रैक करें",
            "स्थिति",
        ],
        "RAISE_GRIEVANCE": [
            "grievance",
            "complaint",
            "problem",
            "issue",
            "delay",
            "pending",
            "stuck",
            "not working",
            "help me",
            "ಖಾಸಗಿ",
            "ದೂರು",
            "ಬಾಕಿ",
            "ವಿಳಂಬ",
            "ಶಿಕಾಯತ್",
            "शिकायत",
            "समस्या",
            "लंबित",
            "इंतजार",
        ],
        "ELIGIBILITY_CHECK": [
            "can i get",
            "am i eligible",
            "eligible for",
            "qualify",
            "eligibility",
            "can i apply",
            "ಯೋಗ್ಯ",
            "ಅರ್ಹತೆ",
            "पात्र",
            "योग्यता",
        ],
        "DOCUMENT_REQUIREMENTS": [
            "documents needed",
            "documents required",
            "what documents",
            "required documents",
            "document checklist",
            "what do i need",
            "documents for",
            "ಡಾಕ್ಯುಮೆಂಟ್ಸ್",
            "ಅಗತ್ಯ ಡಾಕ್ಯುಮೆಂಟ್ಸ್",
            "दस्तावेज़",
            "क्या चाहिए",
        ],
        "SERVICE_DISCOVERY": [
            "what services",
            "list services",
            "available services",
            "what can i",
            "services available",
            "services for",
            "how to get",
            "ಸೇವೆಗಳು",
            "ಸೇವೆ",
            "सेवाएं",
            "क्या उपलब्ध है",
        ],
        "GENERAL_SERVICE_INFORMATION": [
            "tell me about",
            "information about",
            "details about",
            "what is",
            "how does",
            "explain",
            "about the service",
            "ಮಾಹಿತಿ",
            "विवरण",
            "जानकारी",
        ],
    }

    SERVICE_KEYWORDS = {
        "income certificate": ["income", "income certificate", "salary", "income proof", "ಆದಾಯ", "आय"],
        "birth certificate": ["birth", "birth certificate", "born", "ಜನನ", "जन्म"],
        "driving licence": ["driving", "licence", "license", "driver", "ಚಾಲನ", "ड्राइविंग"],
        "passport": ["passport", "ಪಾಸ್‌ಪೋರ್ಟ್", "पासपोर्ट"],
        "government id": ["government id", "govt id", "id card", "identity", "ಸರ್ಕಾರ ID", "सरकारी ID"],
        "address update": ["address", "change address", "update address", "ವಾಸಸ್ಥಳ", "पता"],
    }

    def __init__(self, language_detector: Optional[LanguageDetector] = None):
        self.language_detector = language_detector or RuleBasedLanguageDetector()

    def parse(self, message: str, context: Optional[IntentContext] = None) -> Intent:
        """Parse a message into a structured intent using rules."""
        if not message or not message.strip():
            return Intent(
                intent="CLARIFICATION_REQUIRED",
                service_query="",
                operation="CLARIFICATION_REQUIRED",
                confidence=0.0,
                clarification_required=True,
                clarification_questions=["Please provide a message describing what you need."],
            )

        message = message.strip()
        context = context or IntentContext()

        detected_language, lang_confidence = self.language_detector.detect(message)
        if context.language:
            detected_language = context.language

        intent_type, intent_confidence = self._detect_intent(message)
        service_query, service_confidence = self._extract_service_query(message)

        jurisdiction = self._extract_jurisdiction(message, context)

        overall_confidence = (intent_confidence + service_confidence + lang_confidence) / 3

        if intent_type == "CLARIFICATION_REQUIRED":
            return Intent(
                intent="CLARIFICATION_REQUIRED",
                service_query=service_query,
                operation="CLARIFICATION_REQUIRED",
                jurisdiction=jurisdiction,
                language=detected_language,
                confidence=overall_confidence,
                clarification_required=True,
                clarification_questions=["I'm not sure what you need. Could you please rephrase your request?"],
            )

        if not service_query:
            if intent_type == "SERVICE_DISCOVERY":
                service_query = message
            elif intent_type == "GENERAL_SERVICE_INFORMATION":
                service_query = message
            else:
                return Intent(
                    intent="CLARIFICATION_REQUIRED",
                    service_query=service_query,
                    operation="CLARIFICATION_REQUIRED",
                    jurisdiction=jurisdiction,
                    language=detected_language,
                    confidence=overall_confidence,
                    clarification_required=True,
                    clarification_questions=["Which government service are you referring to?"],
                )

        return Intent(
            intent=intent_type,
            service_query=service_query,
            operation=intent_type,
            jurisdiction=jurisdiction,
            language=detected_language,
            confidence=overall_confidence,
        )

    def _detect_intent(self, message: str) -> tuple:
        """Detect the intent type from a message."""
        message_lower = message.lower()

        for intent_type, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in message_lower:
                    return intent_type, 0.85

        return "SERVICE_DISCOVERY", 0.4

    def _extract_service_query(self, message: str) -> tuple:
        """Extract the service query from a message."""
        message_lower = message.lower()

        for service_name, keywords in self.SERVICE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    return service_name, 0.8

        words = message_lower.split()
        if len(words) > 2:
            for i in range(len(words)):
                for length in [3, 2, 1]:
                    if i + length <= len(words):
                        candidate = " ".join(words[i:i + length])
                        if len(candidate) > 3:
                            return candidate, 0.5

        return message_lower, 0.3

    def _extract_jurisdiction(self, message: str, context: IntentContext) -> "Jurisdiction":
        """Extract jurisdiction from message or context."""
        from packages.services.intent.models import Jurisdiction

        country = context.country
        state = context.state
        district = context.district

        message_lower = message.lower()

        states = [
            "karnataka", "maharashtra", "tamil nadu", "kerala", "andhra pradesh",
            "telangana", "uttar pradesh", "rajasthan", "madhya pradesh", "west bengal",
            "gujarat", "punjab", "haryana", "bihar", "odisha", "assam", "jharkhand",
            "chhattisgarh", "uttarakhand", "himachal pradesh", "goa", "manipur",
            "meghalaya", "nagaland", "tripura", "sikkim", "arunachal pradesh",
            "mizoram", "mumbai", "bangalore", "bengaluru", "delhi", "chennai",
            "hyderabad", "pune", "kolkata", "ahmedabad", "jaipur", "lucknow",
        ]

        for s in states:
            if s in message_lower:
                state = s.title()
                break

        if not country:
            country = "India"

        return Jurisdiction(country=country, state=state, district=district)
