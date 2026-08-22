import pytest
from packages.services.intent import (
    LanguageService,
    RuleBasedLanguageDetector,
    RuleBasedTranslationProvider,
    Language,
    TranslationResult,
)
from packages.services.intent.language import RuleBasedLanguageDetector as Detector


class TestLanguageDetection:
    def test_detect_english(self):
        detector = Detector()
        lang, confidence = detector.detect("I want to apply for an income certificate")
        assert lang == Language.ENGLISH
        assert confidence > 0.5

    def test_detect_kannada(self):
        detector = Detector()
        lang, confidence = detector.detect("ನನ್ನ ಆದಾಯ ಹಣದ ದಾಖಲೆ ಅರ್ಜಿ ಬಾಕಿದ있습니다")
        assert lang == Language.KANNADA
        assert confidence > 0.5

    def test_detect_hindi(self):
        detector = Detector()
        lang, confidence = detector.detect("मेरा आय प्रमाण पत्र आवेदन लंबित है")
        assert lang == Language.HINDI
        assert confidence > 0.5

    def test_detect_mixed_english(self):
        detector = Detector()
        lang, confidence = detector.detect("I want to apply for income certificate in Karnataka")
        assert lang == Language.ENGLISH

    def test_detect_empty(self):
        detector = Detector()
        lang, confidence = detector.detect("")
        assert lang == Language.ENGLISH
        assert confidence == 0.0


class TestTranslationProvider:
    @pytest.fixture
    def provider(self):
        return RuleBasedTranslationProvider()

    @pytest.mark.asyncio
    async def test_translate_known_phrase_en_to_kn(self, provider):
        result = await provider.translate(
            "My application is pending.",
            Language.ENGLISH,
            Language.KANNADA,
        )
        assert result.target_language == Language.KANNADA
        assert result.confidence > 0.0

    @pytest.mark.asyncio
    async def test_translate_known_phrase_en_to_hi(self, provider):
        result = await provider.translate(
            "My application was rejected.",
            Language.ENGLISH,
            Language.HINDI,
        )
        assert result.target_language == Language.HINDI
        assert result.confidence > 0.0

    @pytest.mark.asyncio
    async def test_translate_unknown_returns_original(self, provider):
        result = await provider.translate(
            "Some random text",
            Language.ENGLISH,
            Language.KANNADA,
        )
        assert result.text == "Some random text"
        assert result.confidence == 0.0

    def test_supported_languages(self, provider):
        langs = provider.supported_languages()
        assert Language.ENGLISH in langs
        assert Language.KANNADA in langs
        assert Language.HINDI in langs


class TestLanguageService:
    @pytest.fixture
    def service(self):
        return LanguageService(
            detector=RuleBasedLanguageDetector(),
            translation_provider=RuleBasedTranslationProvider(),
        )

    def test_detect(self, service):
        lang, conf = service.detect("My application is pending")
        assert lang == Language.ENGLISH

    @pytest.mark.asyncio
    async def test_translate(self, service):
        result = await service.translate(
            "My application is pending.",
            Language.ENGLISH,
            Language.KANNADA,
        )
        assert isinstance(result, TranslationResult)

    def test_get_localized_label_en(self, service):
        text = service.get_localized_label("grievance_created", Language.ENGLISH)
        assert "Grievance created" in text

    def test_get_localized_label_kn(self, service):
        text = service.get_localized_label("grievance_created", Language.KANNADA)
        assert "ಖಾಸಗಿ" in text

    def test_get_localized_label_hi(self, service):
        text = service.get_localized_label("grievance_created", Language.HINDI)
        assert "शिकायत" in text

    def test_get_localized_label_with_params(self, service):
        text = service.get_localized_label("grievance_submitted", Language.ENGLISH, ref="REF123")
        assert "REF123" in text

    def test_supported_languages(self, service):
        langs = service.supported_languages
        assert len(langs) == 3