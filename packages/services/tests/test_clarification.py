import pytest
from packages.services.clarification import ClarificationEngine
from packages.ai import MockLLMProvider, LLMClient
from packages.services.intent import IntentType


class TestClarificationEngine:
    @pytest.fixture
    def engine(self):
        return ClarificationEngine()

    def test_generate_new_application(self, engine):
        questions = engine.generate(IntentType.NEW_APPLICATION)
        assert len(questions) >= 1
        assert any("service" in q.lower() for q in questions)

    def test_generate_track_application(self, engine):
        questions = engine.generate(IntentType.TRACK_APPLICATION)
        assert any("reference" in q.lower() for q in questions)

    def test_generate_raise_grievance(self, engine):
        questions = engine.generate(IntentType.RAISE_GRIEVANCE)
        assert any("grievance" in q.lower() or "issue" in q.lower() for q in questions)

    def test_generate_with_missing_fields(self, engine):
        questions = engine.generate(IntentType.NEW_APPLICATION, missing_fields=["date_of_birth"])
        assert any("date of birth" in q.lower() for q in questions)

    def test_generate_limits_to_three(self, engine):
        questions = engine.generate(IntentType.NEW_APPLICATION, missing_fields=["a", "b", "c", "d", "e"])
        assert len(questions) <= 3

    def test_localize_kannada(self, engine):
        questions = engine.generate(
            IntentType.NEW_APPLICATION,
            language="kn",
        )
        assert any("ಸೇವೆ" in q for q in questions)

    def test_localize_hindi(self, engine):
        questions = engine.generate(
            IntentType.NEW_APPLICATION,
            language="hi",
        )
        assert any("सेवा" in q for q in questions)

    @pytest.mark.asyncio
    async def test_generate_with_llm(self, engine):
        provider = MockLLMProvider()
        client = LLMClient(provider=provider)
        engine_with_llm = ClarificationEngine(llm_client=client)

        questions = await engine_with_llm.generate_with_llm(
            "I want to apply",
            missing_fields=["service"],
            language="en",
        )
        assert len(questions) >= 1