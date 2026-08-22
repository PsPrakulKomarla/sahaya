"""LLM Client — high-level interface combining provider, safety, and validation."""
from __future__ import annotations

from typing import Any, TypeVar

from packages.ai.schemas import (
    LLMRequest,
    LLMResponse,
    BaseModel,
    IntentOutput,
    ClarificationOutput,
    ServiceExplanation,
    GrievanceDraftOutput,
    AgentPlanSuggestion,
    ResponseOutput,
)
from packages.ai.providers import LLMProvider, MockLLMProvider
from packages.ai.safety import LLMSafetyValidator

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """High-level LLM client with safety and structured output support."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        safety_validator: LLMSafetyValidator | None = None,
    ) -> None:
        self._provider = provider or MockLLMProvider()
        self._safety = safety_validator or LLMSafetyValidator()

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    async def generate_intent(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> IntentOutput:
        """Generate structured intent from user message."""
        request = self._safety.create_safe_request(
            messages=[{"role": "user", "content": message}],
            response_model=IntentOutput,
            context=context,
        )
        response = await self._provider.complete_structured(request, IntentOutput)

        check = self._safety.validate_response(
            LLMResponse(content=response.model_dump_json(), model=self._provider.model_name)
        )
        if not check.safe:
            raise ValueError(f"Response failed safety check: {check.concerns}")

        return response

    async def generate_clarification(
        self,
        message: str,
        missing_info: list[str],
        context: dict[str, Any] | None = None,
    ) -> ClarificationOutput:
        """Generate clarification questions."""
        prompt = (
            f"User said: {message}\n"
            f"Missing information: {', '.join(missing_info)}\n"
            "Generate 1-3 concise clarification questions."
        )
        request = self._safety.create_safe_request(
            messages=[{"role": "user", "content": prompt}],
            response_model=ClarificationOutput,
            context=context,
        )
        response = await self._provider.complete_structured(request, ClarificationOutput)
        check = self._safety.validate_response(
            LLMResponse(content=response.model_dump_json(), model=self._provider.model_name)
        )
        if not check.safe:
            raise ValueError(f"Response failed safety check: {check.concerns}")
        return response

    async def explain_service(
        self,
        service_name: str,
        metadata: dict[str, Any],
        language: str = "en",
        context: dict[str, Any] | None = None,
    ) -> ServiceExplanation:
        """Generate service explanation."""
        prompt = (
            f"Explain the service '{service_name}' with metadata: {metadata}\n"
            f"Language: {language}\n"
            "Provide: description, eligibility, required documents, processing time, fees, next steps."
        )
        request = self._safety.create_safe_request(
            messages=[{"role": "user", "content": prompt}],
            response_model=ServiceExplanation,
            context=context,
        )
        response = await self._provider.complete_structured(request, ServiceExplanation)
        check = self._safety.validate_response(
            LLMResponse(content=response.model_dump_json(), model=self._provider.model_name)
        )
        if not check.safe:
            raise ValueError(f"Response failed safety check: {check.concerns}")
        return response

    async def draft_grievance(
        self,
        user_issue: str,
        application_info: dict[str, Any],
        service_info: dict[str, Any],
        jurisdiction: str | None,
        context: dict[str, Any] | None = None,
    ) -> GrievanceDraftOutput:
        """Draft a grievance from structured inputs."""
        prompt = (
            f"User issue: {user_issue}\n"
            f"Application: {application_info}\n"
            f"Service: {service_info}\n"
            f"Jurisdiction: {jurisdiction}\n"
            "Generate a professional grievance draft with subject, description, category, "
            "facts (mark as verified/user_claim/inference), and attachments."
        )
        request = self._safety.create_safe_request(
            messages=[{"role": "user", "content": prompt}],
            response_model=GrievanceDraftOutput,
            context=context,
        )
        response = await self._provider.complete_structured(request, GrievanceDraftOutput)
        check = self._safety.validate_response(
            LLMResponse(content=response.model_dump_json(), model=self._provider.model_name)
        )
        if not check.safe:
            raise ValueError(f"Response failed safety check: {check.concerns}")
        return response

    async def suggest_plan(
        self,
        intent: IntentOutput,
        resolution: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> AgentPlanSuggestion:
        """Suggest agent execution plan."""
        prompt = (
            f"Intent: {intent.model_dump()}\n"
            f"Resolution: {resolution}\n"
            "Suggest a workflow plan with steps, estimated duration, and approval requirements."
        )
        request = self._safety.create_safe_request(
            messages=[{"role": "user", "content": prompt}],
            response_model=AgentPlanSuggestion,
            context=context,
        )
        response = await self._provider.complete_structured(request, AgentPlanSuggestion)
        check = self._safety.validate_response(
            LLMResponse(content=response.model_dump_json(), model=self._provider.model_name)
        )
        if not check.safe:
            raise ValueError(f"Response failed safety check: {check.concerns}")
        return response

    async def generate_response(
        self,
        message: str,
        language: str = "en",
        context: dict[str, Any] | None = None,
    ) -> ResponseOutput:
        """Generate localized user response."""
        prompt = (
            f"Generate a helpful response in language '{language}' for: {message}\n"
            f"Context: {context}\n"
            "Return localized message, action_required flag, and suggested actions."
        )
        request = self._safety.create_safe_request(
            messages=[{"role": "user", "content": prompt}],
            response_model=ResponseOutput,
            context=context,
        )
        response = await self._provider.complete_structured(request, ResponseOutput)
        check = self._safety.validate_response(
            LLMResponse(content=response.model_dump_json(), model=self._provider.model_name)
        )
        if not check.safe:
            raise ValueError(f"Response failed safety check: {check.concerns}")
        return response