from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        logger.info("user_created", user_id=str(user.id))
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        await self.session.execute(update(User).where(User.id == user_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(user_id)

    async def delete(self, user_id: UUID) -> bool:
        result = await self.session.execute(delete(User).where(User.id == user_id))
        return result.rowcount > 0

    async def exists(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        return user is not None