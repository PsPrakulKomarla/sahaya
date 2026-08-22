from abc import ABC, abstractmethod
from typing import Optional, BinaryIO


class DocumentStorage(ABC):
    """Abstract base class for document storage.

    Provides secure storage and retrieval of document files.
    """

    @abstractmethod
    async def store(self, file_content: bytes, file_name: str, content_type: str, user_id: str) -> str:
        """Store a document file.

        Args:
            file_content: Raw file bytes.
            file_name: Original file name.
            content_type: MIME type of the file.
            user_id: ID of the user owning the document.

        Returns:
            Storage reference string for retrieving the document.
        """
        pass

    @abstractmethod
    async def retrieve_authorized(self, storage_reference: str, user_id: str) -> bytes:
        """Retrieve a document file with authorization check.

        Args:
            storage_reference: The storage reference from store().
            user_id: ID of the user requesting retrieval.

        Returns:
            Raw file bytes.

        Raises:
            PermissionError: If user is not authorized.
            FileNotFoundError: If document not found.
        """
        pass

    @abstractmethod
    async def delete(self, storage_reference: str, user_id: str) -> bool:
        """Delete a document file with authorization check.

        Args:
            storage_reference: The storage reference to delete.
            user_id: ID of the user requesting deletion.

        Returns:
            True if deleted, False otherwise.
        """
        pass

    @abstractmethod
    async def exists(self, storage_reference: str) -> bool:
        """Check if a document exists in storage."""
        pass

    @abstractmethod
    async def get_signed_url(self, storage_reference: str, user_id: str, expires_in_seconds: int = 3600) -> str:
        """Generate a short-lived signed URL for authorized access.

        Args:
            storage_reference: The storage reference.
            user_id: ID of the user.
            expires_in_seconds: URL expiration time.

        Returns:
            Signed URL string.
        """
        pass
