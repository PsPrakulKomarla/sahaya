from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
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

    async def get_active_for_service(self, service_id: UUID, jurisdiction_id: Optional[UUID] = None) -> Optional[Workflow]:
        query = select(Workflow).where(Workflow.service_id == service_id, Workflow.status == "active")
        if jurisdiction_id:
            query = query.where(Workflow.jurisdiction_id == jurisdiction_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_service(self, service_id: UUID) -> List[Workflow]:
        result = await self.session.execute(select(Workflow).where(Workflow.service_id == service_id))
        return list(result.scalars().all())

    async def update(self, workflow_id: UUID, **kwargs) -> Optional[Workflow]:
        await self.session.execute(update(Workflow).where(Workflow.id == workflow_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(workflow_id)

    async def delete(self, workflow_id: UUID) -> bool:
        result = await self.session.execute(delete(Workflow).where(Workflow.id == workflow_id))
        return result.rowcount > 0