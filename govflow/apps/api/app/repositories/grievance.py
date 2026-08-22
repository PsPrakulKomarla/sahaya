from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.grievance import Grievance
from app.core.logging import get_logger

logger = get_logger(__name__)


class GrievanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, grievance: Grievance) -> Grievance:
        self.session.add(grievance)
        await self.session.flush()
        await self.session.refresh(grievance)
        logger.info("grievance_created", grievance_id=str(grievance.id))
        return grievance

    async def get_by_id(self, grievance_id: UUID) -> Optional[Grievance]:
        result = await self.session.execute(select(Grievance).where(Grievance.id == grievance_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Grievance]:
        result = await self.session.execute(select(Grievance).where(Grievance.user_id == user_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_by_application(self, application_id: UUID) -> List[Grievance]:
        result = await self.session.execute(select(Grievance).where(Grievance.application_id == application_id))
        return list(result.scalars().all())

    async def update(self, grievance_id: UUID, **kwargs) -> Optional[Grievance]:
        await self.session.execute(update(Grievance).where(Grievance.id == grievance_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(grievance_id)

    async def delete(self, grievance_id: UUID) -> bool:
        result = await self.session.execute(delete(Grievance).where(Grievance.id == grievance_id))
        return result.rowcount > 0