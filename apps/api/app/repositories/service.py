from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.service import Service
from app.core.logging import get_logger

logger = get_logger(__name__)


class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, service: Service) -> Service:
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        logger.info("service_created", service_id=str(service.id))
        return service

    async def get_by_id(self, service_id: UUID) -> Optional[Service]:
        result = await self.session.execute(select(Service).where(Service.id == service_id))
        return result.scalar_one_or_none()

    async def get_by_service_id(self, service_id: str) -> Optional[Service]:
        result = await self.session.execute(select(Service).where(Service.service_id == service_id))
        return result.scalar_one_or_none()

    async def list_services(self, enabled_only: bool = True, skip: int = 0, limit: int = 100) -> List[Service]:
        query = select(Service)
        if enabled_only:
            query = query.where(Service.enabled == True)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_by_jurisdiction(self, jurisdiction_id: UUID) -> List[Service]:
        result = await self.session.execute(select(Service).where(Service.jurisdiction_id == jurisdiction_id))
        return list(result.scalars().all())

    async def update(self, service_id: UUID, **kwargs) -> Optional[Service]:
        await self.session.execute(update(Service).where(Service.id == service_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(service_id)

    async def delete(self, service_id: UUID) -> bool:
        result = await self.session.execute(delete(Service).where(Service.id == service_id))
        return result.rowcount > 0