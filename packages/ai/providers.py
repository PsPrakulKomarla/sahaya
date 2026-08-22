"""LLM Provider abstraction."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from packages.ai.schemas import LLMRequest, LLMResponse, BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse: ...

    @abstractmethod
    async def complete_structured(
        self,
        request: LLMRequest,
        response_model: type[T],
    ) -> T: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @property
    @abstractmethod
    def supports_structured_output(self) -> bool: ...


class MockLLMProvider(LLMProvider):
    """Deterministic mock LLM provider for testing."""

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self._responses = responses or {}
        self._call_log: list[LLMRequest] = []

    @property
    def model_name(self) -> str:
        return "mock-llm"

    @property
    def supports_structured_output(self) -> bool:
        return True

    async def complete(self, request: LLMRequest) -> LLMResponse:
        self._call_log.append(request)

        last_msg = request.messages[-1].content if request.messages else ""
        response_text = self._responses.get(last_msg, "Mock response")

        return LLMResponse(
            content=response_text,
            model=self.model_name,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

    async def complete_structured(
        self,
        request: LLMRequest,
        response_model: type[T],
    ) -> T:
        self._call_log.append(request)

        if response_model.__name__ == "IntentOutput":
            return response_model(
                intent="RAISE_GRIEVANCE",
                service_query="income_certificate",
                operation="RAISE_GRIEVANCE",
                language="en",
            )
        elif response_model.__name__ == "ClarificationOutput":
            return response_model(
                questions=["Which service are you referring to?"],
                context_summary="User needs clarification",
            )
        elif response_model.__name__ == "ServiceExplanation":
            return response_model(
                service_name="Income Certificate",
                description="A document certifying annual income",
                required_documents=["ID proof", "Address proof"],
            )
        elif response_model.__name__ == "GrievanceDraftOutput":
            return response_model(
                subject="Application Delay",
                description="Application pending beyond expected time",
                category="APPLICATION_DELAY",
            )
        elif response_model.__name__ == "AgentPlanSuggestion":
            return response_model(
                steps=[{"type": "TRACK_APPLICATION", "description": "Check status"}],
            )
        elif response_model.__name__ == "ResponseOutput":
            return response_model(
                message="I understand. Let me help you.",
                language="en",
            )
        elif response_model.__name__ == "SafetyCheckOutput":
            return response_model(
                safe=True,
                risk_level="low",
                recommended_action="allow",
            )

        return response_model()

    def set_response(self, prompt: str, response: str) -> None:
        self._responses[prompt] = response

    def get_call_log(self) -> list[LLMRequest]:
        return self._call_log.copy()