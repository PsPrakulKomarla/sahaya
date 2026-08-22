from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.jurisdiction import Jurisdiction
from app.core.logging import get_logger

logger = get_logger(__name__)


class JurisdictionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, jurisdiction: Jurisdiction) -> Jurisdiction:
        self.session.add(jurisdiction)
        await self.session.flush()
        await self.session.refresh(jurisdiction)
        logger.info("jurisdiction_created", jurisdiction_id=str(jurisdiction.id))
        return jurisdiction

    async def get_by_id(self, jurisdiction_id: UUID) -> Optional[Jurisdiction]:
        result = await self.session.execute(select(Jurisdiction).where(Jurisdiction.id == jurisdiction_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Jurisdiction]:
        result = await self.session.execute(select(Jurisdiction).where(Jurisdiction.code == code))
        return result.scalar_one_or_none()

    async def list_jurisdictions(self, country: Optional[str] = None, state: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Jurisdiction]:
        query = select(Jurisdiction)
        if country:
            query = query.where(Jurisdiction.country == country)
        if state:
            query = query.where(Jurisdiction.state == state)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, jurisdiction_id: UUID, **kwargs) -> Optional[Jurisdiction]:
        await self.session.execute(update(Jurisdiction).where(Jurisdiction.id == jurisdiction_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(jurisdiction_id)

    async def delete(self, jurisdiction_id: UUID) -> bool:
        result = await self.session.execute(delete(Jurisdiction).where(Jurisdiction.id == jurisdiction_id))
        return result.rowcount > 0