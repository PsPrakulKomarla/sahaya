import hashlib
import os
import uuid
from pathlib import Path
from typing import Optional
from packages.documents.base.document_storage import DocumentStorage
from app.core.logging import get_logger

logger = get_logger(__name__)


class FilesystemStorage(DocumentStorage):
    """Local filesystem document storage.

    Stores documents in a configured directory with user-based isolation.
    Suitable for development and testing.
    """

    def __init__(self, base_path: str = "./storage/documents"):
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def _user_dir(self, user_id: str) -> Path:
        user_dir = self._base_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _get_storage_ref(self, user_id: str, file_name: str) -> str:
        unique_name = f"{uuid.uuid4().hex}_{file_name}"
        return f"{user_id}/{unique_name}"

    async def store(self, file_content: bytes, file_name: str, content_type: str, user_id: str) -> str:
        storage_ref = self._get_storage_ref(user_id, file_name)
        file_path = self._base_path / storage_ref
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_bytes(file_content)

        file_hash = hashlib.sha256(file_content).hexdigest()
        logger.info(
            "document_stored",
            user_id=user_id,
            storage_ref=storage_ref,
            file_size=len(file_content),
            file_hash=file_hash,
        )

        return storage_ref

    async def retrieve_authorized(self, storage_reference: str, user_id: str) -> bytes:
        if not storage_reference.startswith(user_id + "/"):
            logger.warning(
                "unauthorized_document_access",
                user_id=user_id,
                storage_reference=storage_reference,
            )
            raise PermissionError("Unauthorized access to document")

        file_path = self._base_path / storage_reference
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {storage_reference}")

        return file_path.read_bytes()

    async def delete(self, storage_reference: str, user_id: str) -> bool:
        if not storage_reference.startswith(user_id + "/"):
            logger.warning(
                "unauthorized_document_delete",
                user_id=user_id,
                storage_reference=storage_reference,
            )
            return False

        file_path = self._base_path / storage_reference
        if file_path.exists():
            file_path.unlink()
            logger.info("document_deleted", storage_reference=storage_reference)
            return True
        return False

    async def exists(self, storage_reference: str) -> bool:
        file_path = self._base_path / storage_reference
        return file_path.exists()

    async def get_signed_url(self, storage_reference: str, user_id: str, expires_in_seconds: int = 3600) -> str:
        if not storage_reference.startswith(user_id + "/"):
            raise PermissionError("Unauthorized access to document")

        file_path = self._base_path / storage_reference
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {storage_reference}")

        return f"file://{file_path.absolute()}?expires={expires_in_seconds}&user={user_id}"
