from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_task import AgentTask
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: AgentTask) -> AgentTask:
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        logger.info("agent_task_created", task_id=str(task.id))
        return task

    async def get_by_id(self, task_id: UUID) -> Optional[AgentTask]:
        result = await self.session.execute(select(AgentTask).where(AgentTask.id == task_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AgentTask]:
        result = await self.session.execute(select(AgentTask).where(AgentTask.user_id == user_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[AgentTask]:
        result = await self.session.execute(select(AgentTask).where(AgentTask.status == status).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, task_id: UUID, **kwargs) -> Optional[AgentTask]:
        await self.session.execute(update(AgentTask).where(AgentTask.id == task_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(task_id)

    async def delete(self, task_id: UUID) -> bool:
        result = await self.session.execute(delete(AgentTask).where(AgentTask.id == task_id))
        return result.rowcount > 0