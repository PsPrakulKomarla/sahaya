"""Workflow memory domain models.

These are pure Python domain models (not DB models) that represent
learnable workflows with semantic steps, confidence tracking, and
version management. They are used by the WorkflowMemoryService and
LearningPipeline.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    LEARNING = "learning"
    VALIDATED = "validated"
    ACTIVE = "active"
    OUTDATED = "outdated"
    DISABLED = "disabled"
    FAILED = "failed"


class WorkflowSource(str, Enum):
    EXPLORATION = "exploration"
    MANUAL = "manual"
    RECOVERY = "recovery"
    IMPORTED = "imported"


class BrowserActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    UPLOAD = "upload"
    EXTRACT = "extract"
    WAIT = "wait"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    GO_BACK = "go_back"
    HOVER = "hover"
    CHECK = "check"
    UNCHECK = "uncheck"
    KEYS = "keys"


class TargetDescriptor(BaseModel):
    """Semantic description of a browser action target.

    Identifies elements by role, text, and description rather than
    relying solely on CSS/XPath selectors.
    """

    role: Optional[str] = None
    text: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    aria_label: Optional[str] = None
    selector_hint: Optional[str] = None
    input_type: Optional[str] = None
    placeholder: Optional[str] = None

    def semantic_signature(self) -> str:
        parts = []
        if self.role:
            parts.append(f"role={self.role.lower()}")
        if self.text:
            parts.append(f"text={self.text.lower().strip()}")
        if self.label:
            parts.append(f"label={self.label.lower().strip()}")
        if self.aria_label:
            parts.append(f"aria={self.aria_label.lower().strip()}")
        if self.description:
            parts.append(f"desc={self.description.lower().strip()}")
        return "|".join(parts) if parts else "unknown"


class ExpectedResult(BaseModel):
    """Expected outcome after executing a workflow step."""

    url_changed: bool = False
    expected_url_pattern: Optional[str] = None
    expected_heading: Optional[str] = None
    expected_element_role: Optional[str] = None
    expected_element_text: Optional[str] = None
    expected_form_appears: bool = False
    expected_text_contains: Optional[str] = None
    description: str = ""


class RetryPolicy(BaseModel):
    """Retry configuration for a workflow step."""

    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0


class LearnableWorkflowStep(BaseModel):
    """A single step in a learnable workflow.

    Each step captures the browser action, semantic target description,
    expected result, and confidence. This is the core unit of workflow memory.
    """

    step_id: str
    action: BrowserActionType
    purpose: str = ""
    target_description: str = ""
    target: TargetDescriptor = Field(default_factory=TargetDescriptor)
    input_value: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    expected_result: ExpectedResult = Field(default_factory=ExpectedResult)
    confidence: float = 1.0
    optional: bool = False
    requires_human_approval: bool = False
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    selector_hint: Optional[str] = None
    alternatives: List[TargetDescriptor] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowMatch(BaseModel):
    """Result of matching a stored workflow to a context."""

    workflow_id: str
    service_id: str
    jurisdiction_id: Optional[str] = None
    match_score: float = 0.0
    confidence: float = 0.0
    workflow_version: str = ""
    status: str = ""
    reason: str = ""


class WorkflowDefinition(BaseModel):
    """Complete workflow definition stored in memory."""

    workflow_id: Optional[str] = None
    service_id: str
    jurisdiction_id: Optional[str] = None
    service_name: str = ""
    operation: str = ""
    workflow_version: str = "1.0.0"
    status: WorkflowStatus = WorkflowStatus.DRAFT
    source: WorkflowSource = WorkflowSource.EXPLORATION
    steps: List[LearnableWorkflowStep] = Field(default_factory=list)
    confidence: float = 0.0
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    recovery_count: int = 0
    last_verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to a dict suitable for JSONB storage."""
        return {
            "service_id": self.service_id,
            "jurisdiction_id": self.jurisdiction_id,
            "service_name": self.service_name,
            "operation": self.operation,
            "workflow_version": self.workflow_version,
            "status": self.status.value,
            "source": self.source.value,
            "steps": [s.model_dump() for s in self.steps],
            "confidence": self.confidence,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "recovery_count": self.recovery_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_db_dict(cls, data: Dict[str, Any], workflow_id: Optional[str] = None) -> "WorkflowDefinition":
        """Reconstruct from DB-stored dict."""
        steps = []
        for s in data.get("steps", []):
            if isinstance(s, dict):
                steps.append(LearnableWorkflowStep(**s))
            else:
                steps.append(s)
        return cls(
            workflow_id=workflow_id or data.get("workflow_id"),
            service_id=data.get("service_id", ""),
            jurisdiction_id=data.get("jurisdiction_id"),
            service_name=data.get("service_name", ""),
            operation=data.get("operation", ""),
            workflow_version=data.get("workflow_version", "1.0.0"),
            status=WorkflowStatus(data.get("status", "draft")),
            source=WorkflowSource(data.get("source", "exploration")),
            steps=steps,
            confidence=data.get("confidence", 0.0),
            execution_count=data.get("execution_count", 0),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            recovery_count=data.get("recovery_count", 0),
            metadata=data.get("metadata", {}),
        )
