"""Workflow and step models for the agent planner.

These models define the structure of a workflow plan and its individual steps.
They are strongly typed and extensible — new step types can be added without
modifying existing code.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Supported workflow step types.

    New step types can be added here without modifying the planner or executor.
    """
    DISCOVER_SERVICE = "DISCOVER_SERVICE"
    GET_REQUIREMENTS = "GET_REQUIREMENTS"
    CHECK_ELIGIBILITY = "CHECK_ELIGIBILITY"
    VALIDATE_DOCUMENTS = "VALIDATE_DOCUMENTS"
    PREPARE_APPLICATION = "PREPARE_APPLICATION"
    UPDATE_RECORD = "UPDATE_RECORD"
    RENEW = "RENEW"
    BROWSER_EXECUTION = "BROWSER_EXECUTION"
    EXTRACT_DATA = "EXTRACT_DATA"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    SUBMIT = "SUBMIT"
    TRACK_APPLICATION = "TRACK_APPLICATION"
    RAISE_GRIEVANCE = "RAISE_GRIEVANCE"
    COMPLETE = "COMPLETE"


class StepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"


class RetryPolicy(BaseModel):
    """Retry policy for a workflow step."""
    max_retries: int = 0
    retryable: bool = False
    backoff_seconds: float = 1.0


class WorkflowStep(BaseModel):
    """A single step in a workflow plan.

    Each step is strongly typed and supports dependencies, retry policy,
    and approval requirements.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: StepType
    description: str = ""
    dependencies: List[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_seconds: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_ready(self, completed_steps: set) -> bool:
        """Check if all dependencies are satisfied."""
        return set(self.dependencies).issubset(completed_steps)

    def mark_running(self) -> None:
        self.status = StepStatus.RUNNING

    def mark_completed(self, output: Optional[Dict[str, Any]] = None) -> None:
        self.status = StepStatus.COMPLETED
        if output:
            self.output_data = output

    def mark_failed(self, error: Optional[Dict[str, Any]] = None) -> None:
        self.status = StepStatus.FAILED
        if error:
            self.output_data["error"] = error

    def mark_waiting_approval(self) -> None:
        self.status = StepStatus.WAITING_FOR_APPROVAL


class WorkflowPlan(BaseModel):
    """A complete workflow plan consisting of ordered steps.

    The planner produces a WorkflowPlan from intent + service resolution.
    The executor runs the plan step by step.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    service_id: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get all steps that are ready to execute (pending + dependencies met)."""
        completed = {
            s.id for s in self.steps if s.status == StepStatus.COMPLETED
        }
        return [
            s for s in self.steps
            if s.status == StepStatus.PENDING and s.is_ready(completed)
        ]

    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get the next step to execute."""
        ready = self.get_ready_steps()
        return ready[0] if ready else None

    def is_complete(self) -> bool:
        """Check if all steps are completed or skipped."""
        return all(
            s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
            for s in self.steps
        )

    def has_failed_steps(self) -> bool:
        """Check if any steps have failed."""
        return any(s.status == StepStatus.FAILED for s in self.steps)

    def mark_step_completed(self, step_id: str, output: Optional[Dict[str, Any]] = None) -> None:
        """Mark a step as completed."""
        step = self.get_step(step_id)
        if step:
            step.mark_completed(output)

    def mark_step_failed(self, step_id: str, error: Optional[Dict[str, Any]] = None) -> None:
        """Mark a step as failed."""
        step = self.get_step(step_id)
        if step:
            step.mark_failed(error)

    def get_approval_steps(self) -> List[WorkflowStep]:
        """Get all steps requiring approval."""
        return [s for s in self.steps if s.requires_approval]

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the plan."""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "service_id": self.service_id,
            "total_steps": len(self.steps),
            "completed": sum(1 for s in self.steps if s.status == StepStatus.COMPLETED),
            "pending": sum(1 for s in self.steps if s.status == StepStatus.PENDING),
            "failed": sum(1 for s in self.steps if s.status == StepStatus.FAILED),
            "is_complete": self.is_complete(),
        }
