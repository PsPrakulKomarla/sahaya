import asyncio
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger

from packages.documents.base.document_extractor import DocumentExtractor
from packages.documents.base.document_storage import DocumentStorage
from packages.documents.base.document_validator import DocumentValidator
from packages.documents.base.models import (
    DocumentPipelineStatus,
    DocumentProcessingResult,
    FieldSource,
)
from packages.documents.base.ocr_provider import OCRProvider

logger = get_logger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/tiff",
    "image/bmp",
}

MAX_FILE_SIZE_MB = 20
BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".ps1", ".vbs", ".js", ".php", ".py"}


class DocumentService:
    """Core document processing service.

    Orchestrates the document pipeline:
    UPLOAD -> VALIDATE -> OCR -> EXTRACT -> VALIDATE FIELDS -> REVIEW -> VERIFIED

    This service does NOT depend on any specific OCR provider.
    Providers are injected via constructor.
    """

    def __init__(
        self,
        ocr_provider: OCRProvider,
        extractor: DocumentExtractor,
        validator: DocumentValidator,
        storage: DocumentStorage,
        ocr_confidence_threshold: float = 0.8,
    ):
        self._ocr = ocr_provider
        self._extractor = extractor
        self._validator = validator
        self._storage = storage
        self._ocr_confidence_threshold = ocr_confidence_threshold

    def validate_file_upload(
        self,
        file_name: str,
        mime_type: str,
        file_size: int,
    ) -> list[str]:
        """Validate file before upload. Returns list of errors (empty = valid)."""
        errors: list[str] = []

        if mime_type not in ALLOWED_MIME_TYPES:
            errors.append(f"File type '{mime_type}' is not allowed. Accepted: {', '.join(ALLOWED_MIME_TYPES)}")

        max_size = MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            errors.append(f"File size ({file_size} bytes) exceeds maximum ({MAX_FILE_SIZE_MB}MB)")

        if file_size == 0:
            errors.append("File is empty")

        ext = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        if ext in BLOCKED_EXTENSIONS:
            errors.append(f"File extension '{ext}' is blocked for security reasons")

        if ".." in file_name or "/" in file_name or "\\" in file_name:
            errors.append("File name contains path traversal characters")

        if len(file_name) > 255:
            errors.append("File name is too long (max 255 characters)")

        return errors

    async def store_document(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: str,
        user_id: str,
        document_type: str,
    ) -> dict[str, Any]:
        """Store a document and return document metadata."""
        errors = self.validate_file_upload(file_name, mime_type, len(file_content))
        if errors:
            raise ValueError(f"File validation failed: {'; '.join(errors)}")

        storage_ref = await self._storage.store(file_content, file_name, mime_type, user_id)
        file_hash = hashlib.sha256(file_content).hexdigest()

        document_id = str(uuid.uuid4())
        logger.info(
            "document_uploaded",
            document_id=document_id,
            user_id=user_id,
            document_type=document_type,
            file_name=file_name,
            file_size=len(file_content),
        )

        return {
            "id": document_id,
            "user_id": user_id,
            "document_type": document_type,
            "file_name": file_name,
            "storage_reference": storage_ref,
            "mime_type": mime_type,
            "file_size": len(file_content),
            "checksum": file_hash,
            "status": DocumentPipelineStatus.UPLOADED.value,
        }

    async def process_document(
        self,
        document_id: str,
        user_id: str,
        storage_reference: str,
        document_type: str,
        file_name: str,
        language: str | None = None,
    ) -> DocumentProcessingResult:
        """Run the full document processing pipeline.

        UPLOAD -> OCR -> EXTRACT -> VALIDATE
        """
        result = DocumentProcessingResult(
            document_id=document_id,
            status=DocumentPipelineStatus.OCR_PROCESSING,
        )

        try:
            file_content = await self._storage.retrieve_authorized(storage_reference, user_id)
            temp_path = f"/tmp/{document_id}_{file_name}"

            await asyncio.to_thread(_write_temp_file, temp_path, file_content)

            try:
                result.status = DocumentPipelineStatus.OCR_PROCESSING
                ocr_result = await self._ocr.process(temp_path, language=language)
                result.ocr_result = ocr_result
                result.confidence = ocr_result.overall_confidence

                result.status = DocumentPipelineStatus.EXTRACTING
                extracted_fields = await self._extractor.extract(
                    ocr_result, document_type
                )
                result.extracted_fields = extracted_fields

                result.status = DocumentPipelineStatus.NEEDS_REVIEW
                validation = await self._validator.validate(extracted_fields, document_type)
                result.validation_result = validation

                if not validation.valid or ocr_result.overall_confidence < self._ocr_confidence_threshold:
                    result.status = DocumentPipelineStatus.NEEDS_REVIEW
                else:
                    result.status = DocumentPipelineStatus.NEEDS_REVIEW

                logger.info(
                    "document_processed",
                    document_id=document_id,
                    status=result.status.value,
                    confidence=result.confidence,
                    field_count=len(extracted_fields),
                )

            finally:
                await asyncio.to_thread(_remove_temp_file, temp_path)

        except (RuntimeError, ValueError, OSError) as e:
            result.status = DocumentPipelineStatus.FAILED
            result.errors.append(str(e))
            logger.error("document_processing_failed", document_id=document_id, error=str(e))

        return result

    async def verify_document(
        self,
        document_id: str,
        user_id: str,
        verified_fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Verify a document after user review.

        User confirms or corrects extracted fields.
        """
        verified_at = datetime.now(timezone.utc)

        for field_name in verified_fields:
            logger.info(
                "field_verified",
                document_id=document_id,
                field=field_name,
                source=FieldSource.USER_PROVIDED.value,
            )

        return {
            "document_id": document_id,
            "user_id": user_id,
            "status": DocumentPipelineStatus.VERIFIED.value,
            "verified_at": verified_at.isoformat(),
            "verified_fields": verified_fields,
        }

    async def reject_document(
        self,
        document_id: str,
        user_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """Reject a document."""
        logger.info(
            "document_rejected",
            document_id=document_id,
            user_id=user_id,
            reason=reason,
        )

        return {
            "document_id": document_id,
            "user_id": user_id,
            "status": DocumentPipelineStatus.REJECTED.value,
            "reason": reason,
        }


def _write_temp_file(path: str, content: bytes) -> None:
    """Write content to a temporary file (blocking I/O)."""
    with open(path, "wb") as f:
        f.write(content)


def _remove_temp_file(path: str) -> None:
    """Remove a temporary file (blocking I/O)."""
    try:
        os.remove(path)
    except OSError:
        pass
