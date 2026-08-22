"""Conversation Context — lightweight context management."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from packages.services.intent.models import Intent, IntentType, Language


@dataclass
class ConversationContext:
    """Lightweight conversation context scoped to authenticated user."""

    user_id: UUID
    language: Language = Language.ENGLISH
    current_task: str | None = None
    current_service: str | None = None
    current_operation: IntentType | None = None
    pending_clarification: list[str] | None = None
    collected_info: dict[str, Any] = field(default_factory=dict)
    active_grievance_id: UUID | None = None
    active_application_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_language(self, language: Language) -> None:
        self.language = language

    def set_task(self, task: str, service: str | None = None, operation: IntentType | None = None) -> None:
        self.current_task = task
        if service:
            self.current_service = service
        if operation:
            self.current_operation = operation

    def set_pending_clarification(self, questions: list[str]) -> None:
        self.pending_clarification = questions

    def clear_pending_clarification(self) -> None:
        self.pending_clarification = None

    def add_info(self, key: str, value: Any) -> None:
        self.collected_info[key] = value

    def get_info(self, key: str, default: Any = None) -> Any:
        return self.collected_info.get(key, default)

    def set_active_grievance(self, grievance_id: UUID) -> None:
        self.active_grievance_id = grievance_id

    def set_active_application(self, application_id: UUID) -> None:
        self.active_application_id = application_id

    def to_intent_context(self) -> Intent:
        """Convert to IntentContext for intent parsing."""
        return Intent(
            intent=IntentType.CLARIFICATION_REQUIRED,
            service_query=self.current_service or "",
            operation=self.current_operation or IntentType.CLARIFICATION_REQUIRED,
            language=self.language,
            conversation_context={
                "current_task": self.current_task,
                "collected_info": self.collected_info,
                "active_grievance_id": str(self.active_grievance_id) if self.active_grievance_id else None,
                "active_application_id": str(self.active_application_id) if self.active_application_id else None,
            },
        )

    def clear(self) -> None:
        """Clear task-specific context (keep user_id and language)."""
        self.current_task = None
        self.current_service = None
        self.current_operation = None
        self.pending_clarification = None
        self.collected_info = {}
        self.active_grievance_id = None
        self.active_application_id = None