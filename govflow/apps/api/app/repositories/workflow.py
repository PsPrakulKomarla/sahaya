from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Workflow
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workflow: Workflow) -> Workflow:
        self.session.add(workflow)
        await self.session.flush()
        await self.session.refresh(workflow)
        logger.info("workflow_created", workflow_id=str(workflow.id))
        return workflow

    async def get_by_id(self, workflow_id: UUID) -> Optional[Workflow]:
        result = await self.session.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalar_one_or_none()

    async def get_active_for_service(
        self, service_id: UUID, jurisdiction_id: Optional[UUID] = None
    ) -> Optional[Workflow]:
        query = select(Workflow).where(
            Workflow.service_id == service_id, Workflow.status == "active"
        )
        if jurisdiction_id:
            query = query.where(Workflow.jurisdiction_id == jurisdiction_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_best_match(
        self,
        service_id: UUID,
        jurisdiction_id: Optional[UUID] = None,
        operation: Optional[str] = None,
    ) -> Optional[Workflow]:
        """Find the best matching active workflow for a service/jurisdiction/operation."""
        query = select(Workflow).where(
            Workflow.service_id == service_id,
            Workflow.status.in_(["active", "validated"]),
        )
        if jurisdiction_id:
            query = query.where(Workflow.jurisdiction_id == jurisdiction_id)
        query = query.order_by(Workflow.confidence.desc(), Workflow.workflow_version.desc())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search(
        self,
        service_id: Optional[UUID] = None,
        jurisdiction_id: Optional[UUID] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Workflow]:
        """Search workflows by criteria."""
        query = select(Workflow)
        if service_id:
            query = query.where(Workflow.service_id == service_id)
        if jurisdiction_id:
            query = query.where(Workflow.jurisdiction_id == jurisdiction_id)
        if status:
            query = query.where(Workflow.status == status)
        if source:
            query = query.where(Workflow.source == source)
        query = query.order_by(Workflow.updated_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_service(self, service_id: UUID) -> List[Workflow]:
        result = await self.session.execute(
            select(Workflow).where(Workflow.service_id == service_id)
        )
        return list(result.scalars().all())

    async def update(self, workflow_id: UUID, **kwargs) -> Optional[Workflow]:
        await self.session.execute(
            update(Workflow).where(Workflow.id == workflow_id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(workflow_id)

    async def delete(self, workflow_id: UUID) -> bool:
        result = await self.session.execute(
            delete(Workflow).where(Workflow.id == workflow_id)
        )
        return result.rowcount > 0

    async def count_by_status(self, service_id: Optional[UUID] = None) -> dict:
        """Count workflows grouped by status."""
        query = select(Workflow.status, func.count(Workflow.id)).group_by(Workflow.status)
        if service_id:
            query = query.where(Workflow.service_id == service_id)
        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}
