import pytest
from packages.services.intent import (
    RuleBasedLanguageDetector,
    RuleBasedIntentEngine,
    LanguageService,
    RuleBasedTranslationProvider,
    Language,
)
from packages.services.registry import ServiceResolver
from packages.services.registry.registry import get_registry, reset_registry
from packages.services.adapters import MockIncomeCertificateAdapter


class TestMultilingualEndToEnd:
    @pytest.fixture
    def setup(self):
        reset_registry()
        registry = get_registry()
        registry.register_service(MockIncomeCertificateAdapter())
        
        detector = RuleBasedLanguageDetector()
        engine = RuleBasedIntentEngine(language_detector=detector)
        resolver = ServiceResolver()
        lang_service = LanguageService(
            detector=detector,
            translation_provider=RuleBasedTranslationProvider(),
        )
        return detector, engine, resolver, lang_service

    @pytest.mark.asyncio
    async def test_english_income_certificate_application(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "I want to apply for an income certificate"

        # Language detection
        lang, conf = detector.detect(message)
        assert lang == Language.ENGLISH

        # Intent parsing
        intent = engine.parse(message)
        assert intent.intent == "NEW_APPLICATION"
        assert intent.service_query == "income certificate"

        # Service resolution
        resolution = await resolver.resolve_intent(intent)
        assert resolution.service_id == "income_certificate"
        assert resolution.status == "RESOLVED"

    @pytest.mark.asyncio
    async def test_kannada_income_certificate_application(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "ನಾನು ಆದಾಯ ಹಣದ ದಾಖಲೆಗಾಗಿ ಅರ್ಜಿ ಮಾಡಲು ಇಚ್ಛಿಸುತ್ತೇನೆ"

        # Language detection
        lang, conf = detector.detect(message)
        assert lang == Language.KANNADA

        # Intent parsing
        intent = engine.parse(message)
        assert intent.intent == "NEW_APPLICATION"
        assert "income" in intent.service_query.lower()

        # Service resolution
        resolution = await resolver.resolve_intent(intent)
        assert resolution.service_id == "income_certificate"

    @pytest.mark.asyncio
    async def test_hindi_income_certificate_application(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "मैं आय प्रमाण पत्र के लिए आवेदन करना चाहता हूँ"

        # Language detection
        lang, conf = detector.detect(message)
        assert lang == Language.HINDI

        # Intent parsing
        intent = engine.parse(message)
        assert intent.intent == "NEW_APPLICATION"
        assert "income" in intent.service_query.lower()

        # Service resolution
        resolution = await resolver.resolve_intent(intent)
        assert resolution.service_id == "income_certificate"

    @pytest.mark.asyncio
    async def test_english_grievance_delay(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "My income certificate application has been pending for two months"

        lang, conf = detector.detect(message)
        assert lang == Language.ENGLISH

        intent = engine.parse(message)
        assert intent.intent == "RAISE_GRIEVANCE"

    @pytest.mark.asyncio
    async def test_kannada_grievance_delay(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "ನನ್ನ ಆದಾಯ ಹಣದ ದಾಖಲೆ ಅರ್ಜಿ ಎರಡು ತಿಂಗಳು ಬಾಕಿ"

        lang, conf = detector.detect(message)
        assert lang == Language.KANNADA

        intent = engine.parse(message)
        assert intent.intent == "RAISE_GRIEVANCE"

    @pytest.mark.asyncio
    async def test_hindi_grievance_delay(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "मेरा आय प्रमाण पत्र आवेदन दो महीने से लंबित है"

        lang, conf = detector.detect(message)
        assert lang == Language.HINDI

        intent = engine.parse(message)
        assert intent.intent == "RAISE_GRIEVANCE"

    @pytest.mark.asyncio
    async def test_english_track_application(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "Check my application status"

        lang, conf = detector.detect(message)
        assert lang == Language.ENGLISH

        intent = engine.parse(message)
        assert intent.intent == "TRACK_APPLICATION"

    @pytest.mark.asyncio
    async def test_kannada_track_application(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "ನನ್ನ ಅರ್ಜಿ ಸ್ಥಿತಿ ಪರಿಶೀಲಿಸಿ"

        lang, conf = detector.detect(message)
        assert lang == Language.KANNADA

        intent = engine.parse(message)
        assert intent.intent == "TRACK_APPLICATION"

    @pytest.mark.asyncio
    async def test_hindi_track_application(self, setup):
        detector, engine, resolver, lang_service = setup
        message = "मेरा आवेदन स्थिति जांचें"

        lang, conf = detector.detect(message)
        assert lang == Language.HINDI

        intent = engine.parse(message)
        assert intent.intent == "TRACK_APPLICATION"

    @pytest.mark.asyncio
    async def test_same_structured_output_across_languages(self, setup):
        """All three languages should produce the same structured intent for equivalent messages."""
        detector, engine, resolver, lang_service = setup

        messages = {
            "en": "I want to apply for an income certificate",
            "kn": "ನಾನು ಆದಾಯ ಹಣದ ದಾಖಲೆಗಾಗಿ ಅರ್ಜಿ ಮಾಡಲು ಇಚ್ಛಿಸುತ್ತೇನೆ",
            "hi": "मैं आय प्रमाण पत्र के लिए आवेदन करना चाहता हूँ",
        }

        results = {}
        for lang_code, message in messages.items():
            intent = engine.parse(message)
            results[lang_code] = {
                "intent": intent.intent,
                "service_query": intent.service_query.lower(),
                "operation": intent.operation,
            }

        # All should have same intent and operation
        assert results["en"]["intent"] == results["kn"]["intent"] == results["hi"]["intent"]
        assert results["en"]["operation"] == results["kn"]["operation"] == results["hi"]["operation"]
        # Service query should resolve to same service
        assert "income" in results["en"]["service_query"]
        assert "income" in results["kn"]["service_query"]
        assert "income" in results["hi"]["service_query"]

    def test_localized_response_generation(self, setup):
        _, _, _, lang_service = setup

        # Test localized labels
        en_text = lang_service.get_localized_label("grievance_created", Language.ENGLISH)
        kn_text = lang_service.get_localized_label("grievance_created", Language.KANNADA)
        hi_text = lang_service.get_localized_label("grievance_created", Language.HINDI)

        assert "Grievance" in en_text
        assert "ಖಾಸಗಿ" in kn_text
        assert "शिकायत" in hi_text

        # Test with parameters
        en_ref = lang_service.get_localized_label("grievance_submitted", Language.ENGLISH, ref="REF123")
        assert "REF123" in en_ref