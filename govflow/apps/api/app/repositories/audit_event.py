from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_event import AuditEvent
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event: AuditEvent) -> AuditEvent:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_by_id(self, event_id: UUID) -> Optional[AuditEvent]:
        result = await self.session.execute(select(AuditEvent).where(AuditEvent.id == event_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditEvent]:
        result = await self.session.execute(select(AuditEvent).where(AuditEvent.user_id == user_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_by_task(self, task_id: UUID) -> List[AuditEvent]:
        result = await self.session.execute(select(AuditEvent).where(AuditEvent.task_id == task_id))
        return list(result.scalars().all())

    async def list_by_event_type(self, event_type: str, skip: int = 0, limit: int = 100) -> List[AuditEvent]:
        result = await self.session.execute(select(AuditEvent).where(AuditEvent.event_type == event_type).offset(skip).limit(limit))
        return list(result.scalars().all())