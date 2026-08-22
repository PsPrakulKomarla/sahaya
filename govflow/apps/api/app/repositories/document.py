from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        logger.info("document_created", document_id=str(document.id))
        return document

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        result = await self.session.execute(select(Document).where(Document.user_id == user_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_by_type(self, user_id: UUID, document_type: str) -> List[Document]:
        result = await self.session.execute(select(Document).where(Document.user_id == user_id, Document.document_type == document_type))
        return list(result.scalars().all())

    async def update(self, document_id: UUID, **kwargs) -> Optional[Document]:
        await self.session.execute(update(Document).where(Document.id == document_id).values(**kwargs))
        await self.session.flush()
        return await self.get_by_id(document_id)

    async def delete(self, document_id: UUID) -> bool:
        result = await self.session.execute(delete(Document).where(Document.id == document_id))
        return result.rowcount > 0