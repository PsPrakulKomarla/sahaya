"""RecoveryMemory — records recovery events and contributes to workflow learning.

After successful recovery, records:
- old workflow step
- failed condition
- replacement target
- page context
- success
- confidence
- timestamp
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.agent.recovery.types import (
    FailureType,
    RecoveryDecision,
    RecoveryDecisionType,
    RecoveryEvent,
    RecoveryLevel,
)


class RecoveryRecord(BaseModel):
    """A single recovery record linking failure to successful resolution."""
    record_id: str = ""
    old_step_id: str = ""
    old_target_text: str = ""
    old_target_role: str = ""
    failure_type: FailureType = FailureType.UNKNOWN_FAILURE
    replacement_text: str = ""
    replacement_selector: Optional[str] = None
    page_url: str = ""
    page_title: str = ""
    success: bool = False
    confidence: float = 0.0
    recovery_level: RecoveryLevel = RecoveryLevel.LEVEL_1_RETRY
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    """Proposed update to a workflow based on recovery."""
    workflow_id: str = ""
    old_version: str = ""
    new_version: str = ""
    updated_steps: List[Dict[str, Any]] = Field(default_factory=list)
    reason: str = ""
    confidence: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecoveryMemory:
    """Records recovery events and contributes to workflow learning.

    After successful recovery, records the old step, failed condition,
    replacement target, and success. This contributes to workflow learning
    by tracking what replacements worked.
    """

    def __init__(self) -> None:
        self._records: List[RecoveryRecord] = []
        self._workflow_updates: List[WorkflowUpdate] = []
        self._success_count: int = 0
        self._failure_count: int = 0

    def record_recovery(
        self,
        step_id: str,
        old_target_text: str,
        old_target_role: str,
        failure_type: FailureType,
        decision: RecoveryDecision,
        page_url: str = "",
        page_title: str = "",
    ) -> RecoveryRecord:
        """Record a recovery attempt result."""
        record = RecoveryRecord(
            record_id=f"rec_{step_id}_{len(self._records)}",
            old_step_id=step_id,
            old_target_text=old_target_text,
            old_target_role=old_target_role,
            failure_type=failure_type,
            replacement_text=decision.candidate_text or "",
            replacement_selector=decision.candidate_selector,
            page_url=page_url,
            page_title=page_title,
            success=decision.decision in (
                RecoveryDecisionType.RECOVER,
                RecoveryDecisionType.RETRY,
            ),
            confidence=decision.confidence,
            recovery_level=decision.recovery_level,
        )
        self._records.append(record)
        if record.success:
            self._success_count += 1
        else:
            self._failure_count += 1
        return record

    def get_records_for_step(self, step_id: str) -> List[RecoveryRecord]:
        """Get all recovery records for a specific step."""
        return [r for r in self._records if r.old_step_id == step_id]

    def get_successful_replacements(self, step_id: str) -> List[RecoveryRecord]:
        """Get successful recovery replacements for a step."""
        return [
            r for r in self._records
            if r.old_step_id == step_id and r.success
        ]

    def suggest_alternative(
        self, step_id: str, target_text: str
    ) -> Optional[RecoveryRecord]:
        """Suggest an alternative target based on past successful recoveries."""
        records = self.get_successful_replacements(step_id)
        for record in records:
            if record.old_target_text != target_text and record.confidence > 0.5:
                return record
        return None

    def record_workflow_update(self, update: WorkflowUpdate) -> None:
        """Record a workflow update triggered by recovery."""
        self._workflow_updates.append(update)

    def get_workflow_updates(self, workflow_id: str) -> List[WorkflowUpdate]:
        """Get all workflow updates for a specific workflow."""
        return [u for u in self._workflow_updates if u.workflow_id == workflow_id]

    def should_update_workflow(
        self, step_id: str, min_successes: int = 2, min_confidence: float = 0.7
    ) -> bool:
        """Check if a workflow should be updated based on recovery history."""
        records = self.get_successful_replacements(step_id)
        if len(records) < min_successes:
            return False
        avg_confidence = sum(r.confidence for r in records) / len(records)
        return avg_confidence >= min_confidence

    @property
    def total_records(self) -> int:
        return len(self._records)

    @property
    def success_rate(self) -> float:
        total = self._success_count + self._failure_count
        if total == 0:
            return 0.0
        return self._success_count / total

    def summary(self) -> Dict[str, Any]:
        """Return a summary of recovery memory state."""
        return {
            "total_records": self.total_records,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "success_rate": round(self.success_rate, 4),
            "workflow_updates": len(self._workflow_updates),
        }
