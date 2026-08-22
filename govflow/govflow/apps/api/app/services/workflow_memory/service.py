"""WorkflowMemoryService - manages the lifecycle of learnable workflows.

Responsibilities:
- Store workflows
- Retrieve workflows
- Search workflows
- Match workflow to service/jurisdiction
- Track workflow version
- Track confidence
- Mark outdated workflows
- Update workflows
- Record successful/failed executions
- Promote workflows through status lifecycle
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.core.logging import get_logger
from app.models.workflow import Workflow
from app.repositories.workflow import WorkflowRepository
from app.services.workflow_memory.models import (
    LearnableWorkflowStep,
    WorkflowDefinition,
    WorkflowMatch,
    WorkflowSource,
    WorkflowStatus,
)

logger = get_logger(__name__)

# Default promotion thresholds
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_MIN_EXECUTIONS = 1
DEFAULT_MIN_SUCCESS_RATE = 0.8


class WorkflowMemoryService:
    """Service for managing learnable workflow memory.

    This service is independent of any browser provider. It operates on
    WorkflowDefinition domain models and persists via WorkflowRepository.
    """

    def __init__(
        self,
        repository: WorkflowRepository,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        min_executions: int = DEFAULT_MIN_EXECUTIONS,
        min_success_rate: float = DEFAULT_MIN_SUCCESS_RATE,
    ):
        self._repo = repository
        self._confidence_threshold = confidence_threshold
        self._min_executions = min_executions
        self._min_success_rate = min_success_rate

    async def save(self, definition: WorkflowDefinition) -> Workflow:
        """Save a new workflow definition."""
        workflow = Workflow(
            service_id=UUID(definition.service_id),
            jurisdiction_id=UUID(definition.jurisdiction_id) if definition.jurisdiction_id else None,
            workflow_version=definition.workflow_version,
            status=definition.status.value,
            source=definition.source.value,
            workflow_definition=definition.to_db_dict(),
            confidence=definition.confidence,
            execution_count=definition.execution_count,
            success_count=definition.success_count,
            failure_count=definition.failure_count,
            recovery_count=definition.recovery_count,
        )
        saved = await self._repo.create(workflow)
        logger.info(
            "workflow_memory_saved",
            workflow_id=str(saved.id),
            service_id=definition.service_id,
            version=definition.workflow_version,
            status=definition.status.value,
        )
        return saved

    async def get(self, workflow_id: UUID) -> Optional[WorkflowDefinition]:
        """Retrieve a workflow definition by ID."""
        workflow = await self._repo.get_by_id(workflow_id)
        if not workflow:
            return None
        return WorkflowDefinition.from_db_dict(
            workflow.workflow_definition, workflow_id=str(workflow.id)
        )

    async def get_raw(self, workflow_id: UUID) -> Optional[Workflow]:
        """Retrieve the raw DB workflow object."""
        return await self._repo.get_by_id(workflow_id)

    async def search(
        self,
        service_id: Optional[str] = None,
        jurisdiction_id: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[WorkflowDefinition]:
        """Search workflows by criteria."""
        svc_uuid = UUID(service_id) if service_id else None
        jur_uuid = UUID(jurisdiction_id) if jurisdiction_id else None
        workflows = await self._repo.search(
            service_id=svc_uuid,
            jurisdiction_id=jur_uuid,
            status=status,
            source=source,
        )
        return [
            WorkflowDefinition.from_db_dict(w.workflow_definition, workflow_id=str(w.id))
            for w in workflows
        ]

    async def find_best_match(
        self,
        service_id: str,
        jurisdiction_id: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> Optional[WorkflowMatch]:
        """Find the best matching active workflow for a service/jurisdiction."""
        svc_uuid = UUID(service_id)
        jur_uuid = UUID(jurisdiction_id) if jurisdiction_id else None
        workflow = await self._repo.get_best_match(
            service_id=svc_uuid, jurisdiction_id=jur_uuid, operation=operation
        )
        if not workflow:
            return None
        return WorkflowMatch(
            workflow_id=str(workflow.id),
            service_id=str(workflow.service_id),
            jurisdiction_id=str(workflow.jurisdiction_id) if workflow.jurisdiction_id else None,
            match_score=workflow.confidence or 0.0,
            confidence=workflow.confidence or 0.0,
            workflow_version=workflow.workflow_version,
            status=workflow.status,
            reason="Best matching active workflow",
        )

    async def create_version(
        self,
        service_id: str,
        definition: WorkflowDefinition,
        jurisdiction_id: Optional[str] = None,
    ) -> Workflow:
        """Create a new version of an existing workflow.

        Generates a new version string based on the current date.
        """
        now = datetime.now(timezone.utc)
        version_tag = f"{now.strftime('%Y.%m')}.{1}"
        definition.workflow_version = version_tag
        definition.status = WorkflowStatus.LEARNING
        definition.updated_at = now
        return await self.save(definition)

    async def promote(self, workflow_id: UUID, target_status: str) -> Optional[Workflow]:
        """Promote a workflow to a new status.

        Validates that the promotion is allowed:
        - DRAFT -> LEARNING -> VALIDATED -> ACTIVE
        - Any -> OUTDATED
        - Any -> DISABLED
        """
        workflow = await self._repo.get_by_id(workflow_id)
        if not workflow:
            return None

        current = workflow.status
        allowed_transitions = {
            "draft": ["learning", "disabled"],
            "learning": ["validated", "draft", "disabled", "failed"],
            "validated": ["active", "learning", "disabled"],
            "active": ["outdated", "disabled"],
            "outdated": ["learning", "disabled"],
            "failed": ["draft", "disabled"],
            "disabled": ["draft"],
        }

        if target_status not in allowed_transitions.get(current, []):
            logger.warning(
                "invalid_promotion",
                workflow_id=str(workflow_id),
                from_status=current,
                to_status=target_status,
            )
            return None

        now = datetime.now(timezone.utc)
        update_kwargs: Dict = {"status": target_status}
        if target_status == "active":
            update_kwargs["last_verified_at"] = now

        updated = await self._repo.update(workflow_id, **update_kwargs)
        logger.info(
            "workflow_promoted",
            workflow_id=str(workflow_id),
            from_status=current,
            to_status=target_status,
        )
        return updated

    async def record_execution(
        self, workflow_id: UUID, success: bool, recovered: bool = False
    ) -> Optional[Workflow]:
        """Record an execution result for a workflow.

        Updates execution counts and confidence.
        """
        workflow = await self._repo.get_by_id(workflow_id)
        if not workflow:
            return None

        now = datetime.now(timezone.utc)
        update_kwargs: Dict = {
            "execution_count": (workflow.execution_count or 0) + 1,
            "last_used_at": now,
        }

        if success:
            update_kwargs["success_count"] = (workflow.success_count or 0) + 1
            update_kwargs["last_success_at"] = now
        else:
            update_kwargs["failure_count"] = (workflow.failure_count or 0) + 1

        if recovered:
            update_kwargs["recovery_count"] = (workflow.recovery_count or 0) + 1

        # Recalculate confidence
        total = (workflow.execution_count or 0) + 1
        successes = (workflow.success_count or 0) + (1 if success else 0)
        new_confidence = successes / total if total > 0 else 0.0
        update_kwargs["confidence"] = round(new_confidence, 4)

        updated = await self._repo.update(workflow_id, **update_kwargs)
        logger.info(
            "workflow_execution_recorded",
            workflow_id=str(workflow_id),
            success=success,
            recovered=recovered,
            new_confidence=update_kwargs["confidence"],
        )
        return updated

    async def mark_outdated(self, workflow_id: UUID, reason: str = "") -> Optional[Workflow]:
        """Mark a workflow as outdated."""
        updated = await self.promote(workflow_id, "outdated")
        if updated and reason:
            logger.info(
                "workflow_marked_outdated",
                workflow_id=str(workflow_id),
                reason=reason,
            )
        return updated

    async def disable(self, workflow_id: UUID) -> Optional[Workflow]:
        """Disable a workflow."""
        return await self.promote(workflow_id, "disabled")

    async def update_confidence(self, workflow_id: UUID, confidence: float) -> Optional[Workflow]:
        """Update the confidence score for a workflow."""
        return await self._repo.update(workflow_id, confidence=confidence)

    async def count_by_status(self, service_id: Optional[str] = None) -> Dict[str, int]:
        """Count workflows grouped by status."""
        svc_uuid = UUID(service_id) if service_id else None
        return await self._repo.count_by_status(service_id=svc_uuid)

    def should_promote_to_active(self, workflow: Workflow) -> bool:
        """Check if a workflow meets criteria for promotion to ACTIVE."""
        total = workflow.execution_count or 0
        successes = workflow.success_count or 0
        confidence = workflow.confidence or 0.0

        if total < self._min_executions:
            return False
        if confidence < self._confidence_threshold:
            return False
        if total > 0 and (successes / total) < self._min_success_rate:
            return False
        return True
