from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import Application, ApplicationTimeline
from app.core.logging import get_logger

logger = get_logger(__name__)


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, application: Application) -> Application:
        self.session.add(application)
        await self.session.flush()
        await self.session.refresh(application)
        logger.info("application_created", application_id=str(application.id))
        return application

    async def get_by_id(self, application_id: UUID) -> Optional[Application]:
        result = await self.session.execute(select(Application).where(Application.id == application_id))
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference_number: str) -> Optional[Application]:
        result = await self.session.execute(select(Application).where(Application.reference_number == reference_number))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        result = await self.session.execute(select(Application).where(Application.user_id == user_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_by_service(self, service_id: UUID, skip: int = 0, limit: int = 100) -> List[Application]:
        result = await self.session.execute(select(Application).where(Application.service_id == service_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, application_id: UUID, **kwargs) -> Optional[Application]:
        await self.session.execute(update(Application).where(Application.id == application_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(application_id)

    async def delete(self, application_id: UUID) -> bool:
        result = await self.session.execute(delete(Application).where(Application.id == application_id))
        return result.rowcount > 0


class ApplicationTimelineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event: ApplicationTimeline) -> ApplicationTimeline:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def list_by_application(self, application_id: UUID) -> List[ApplicationTimeline]:
        result = await self.session.execute(
            select(ApplicationTimeline)
            .where(ApplicationTimeline.application_id == application_id)
            .order_by(ApplicationTimeline.timestamp)
        )
        return list(result.scalars().all())