from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.approval import Approval
from app.core.logging import get_logger

logger = get_logger(__name__)


class ApprovalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, approval: Approval) -> Approval:
        self.session.add(approval)
        await self.session.flush()
        await self.session.refresh(approval)
        logger.info("approval_created", approval_id=str(approval.id))
        return approval

    async def get_by_id(self, approval_id: UUID) -> Optional[Approval]:
        result = await self.session.execute(select(Approval).where(Approval.id == approval_id))
        return result.scalar_one_or_none()

    async def list_pending_for_user(self, user_id: UUID) -> List[Approval]:
        result = await self.session.execute(
            select(Approval).where(Approval.user_id == user_id, Approval.status == "pending")
        )
        return list(result.scalars().all())

    async def list_by_task(self, task_id: UUID) -> List[Approval]:
        result = await self.session.execute(select(Approval).where(Approval.task_id == task_id))
        return list(result.scalars().all())

    async def update(self, approval_id: UUID, **kwargs) -> Optional[Approval]:
        await self.session.execute(update(Approval).where(Approval.id == approval_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(approval_id)

    async def delete(self, approval_id: UUID) -> bool:
        result = await self.session.execute(delete(Approval).where(Approval.id == approval_id))
        return result.rowcount > 0