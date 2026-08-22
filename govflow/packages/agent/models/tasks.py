from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class AgentState(str, Enum):
    """States for the agent state machine."""
    CREATED = "CREATED"
    UNDERSTANDING = "UNDERSTANDING"
    RESOLVING_SERVICE = "RESOLVING_SERVICE"
    PLANNING = "PLANNING"
    VALIDATING = "VALIDATING"
    WAITING_FOR_DOCUMENTS = "WAITING_FOR_DOCUMENTS"
    EXECUTING = "EXECUTING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    SUBMITTING = "SUBMITTING"
    VERIFYING = "VERIFYING"
    TRACKING = "TRACKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECOVERY = "RECOVERY"
    WAITING_FOR_USER = "WAITING_FOR_USER"


class StepType(str, Enum):
    """Types of workflow steps."""
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
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    WAITING = "WAITING"


class TaskStatus(str, Enum):
    """Status of an agent task."""
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskType(str, Enum):
    """Types of agent tasks."""
    NEW_APPLICATION = "NEW_APPLICATION"
    UPDATE_RECORD = "UPDATE_RECORD"
    RENEWAL = "RENEWAL"
    TRACK_APPLICATION = "TRACK_APPLICATION"
    RAISE_GRIEVANCE = "RAISE_GRIEVANCE"
    CHECK_ELIGIBILITY = "CHECK_ELIGIBILITY"
    DISCOVER_SERVICE = "DISCOVER_SERVICE"
    OTHER = "OTHER"


class RetryPolicy(BaseModel):
    """Retry policy for workflow steps."""
    max_retries: int = 0
    retryable: bool = False
    retry_delay_seconds: int = 5


class WorkflowStep(BaseModel):
    """A single step in a workflow plan."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: StepType
    description: str = ""
    dependencies: List[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowPlan(BaseModel):
    """A complete workflow plan for a task."""
    task_type: TaskType
    service_id: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps whose dependencies are all completed."""
        ready = []
        for step in self.steps:
            if step.status != StepStatus.PENDING:
                continue
            deps_met = all(
                self._is_dependency_met(dep_id)
                for dep_id in step.dependencies
            )
            if deps_met:
                ready.append(step)
        return ready

    def _is_dependency_met(self, dep_id: str) -> bool:
        dep = self.get_step(dep_id)
        if dep is None:
            return True
        return dep.status == StepStatus.COMPLETED

    def is_complete(self) -> bool:
        return all(
            s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
            for s in self.steps
        )

    def has_failed(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps)


class ExecutionContext(BaseModel):
    """Context passed to step handlers during execution."""
    task_id: str
    user_id: str
    service_id: str
    jurisdiction: Optional[str] = None
    workflow_id: Optional[str] = None
    current_step: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """Result of a completed task."""
    task_id: str
    status: TaskStatus
    service_id: Optional[str] = None
    operation: Optional[str] = None
    application_id: Optional[str] = None
    reference_number: Optional[str] = None
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    completed_at: Optional[datetime] = None


class AgentTask(BaseModel):
    """An agent task tracking the full lifecycle."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    original_request: str
    intent: Optional[Dict[str, Any]] = None
    resolution: Optional[Dict[str, Any]] = None
    task_type: TaskType = TaskType.OTHER
    service_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    state: AgentState = AgentState.CREATED
    workflow_plan: Optional[WorkflowPlan] = None
    status: TaskStatus = TaskStatus.CREATED
    result: Optional[TaskResult] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
