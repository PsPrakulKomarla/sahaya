import os
import sys
import tempfile
import uuid

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from packages.documents.document_service import DocumentService
from packages.documents.extraction.extractor import DefaultDocumentExtractor
from packages.documents.ocr.mock_provider import MockOCRProvider
from packages.documents.storage.filesystem_storage import FilesystemStorage
from packages.documents.validation.validator import DefaultDocumentValidator


class TestFilesystemStorage:
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            content = b"test document content"
            user_id = str(uuid.uuid4())

            ref = await storage.store(content, "test.pdf", "application/pdf", user_id)
            assert ref
            assert user_id in ref

            retrieved = await storage.retrieve_authorized(ref, user_id)
            assert retrieved == content

    @pytest.mark.asyncio
    async def test_unauthorized_retrieve(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user1 = str(uuid.uuid4())
            user2 = str(uuid.uuid4())

            ref = await storage.store(b"content", "test.pdf", "application/pdf", user1)

            with pytest.raises(PermissionError):
                await storage.retrieve_authorized(ref, user2)

    @pytest.mark.asyncio
    async def test_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user_id = str(uuid.uuid4())
            ref = await storage.store(b"content", "test.pdf", "application/pdf", user_id)

            result = await storage.delete(ref, user_id)
            assert result is True

            exists = await storage.exists(ref)
            assert exists is False

    @pytest.mark.asyncio
    async def test_unauthorized_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user1 = str(uuid.uuid4())
            user2 = str(uuid.uuid4())

            ref = await storage.store(b"content", "test.pdf", "application/pdf", user1)
            result = await storage.delete(ref, user2)
            assert result is False

    @pytest.mark.asyncio
    async def test_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user_id = str(uuid.uuid4())
            ref = await storage.store(b"content", "test.pdf", "application/pdf", user_id)

            assert await storage.exists(ref) is True
            assert await storage.exists("nonexistent/path") is False

    @pytest.mark.asyncio
    async def test_get_signed_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user_id = str(uuid.uuid4())
            ref = await storage.store(b"content", "test.pdf", "application/pdf", user_id)

            url = await storage.get_signed_url(ref, user_id)
            assert url.startswith("file://")

    @pytest.mark.asyncio
    async def test_unauthorized_signed_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user1 = str(uuid.uuid4())
            user2 = str(uuid.uuid4())

            ref = await storage.store(b"content", "test.pdf", "application/pdf", user1)
            with pytest.raises(PermissionError):
                await storage.get_signed_url(ref, user2)


class TestDocumentService:
    def test_validate_file_upload_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            errors = doc_service.validate_file_upload("doc.pdf", "application/pdf", 1024)
            assert len(errors) == 0

    def test_validate_file_upload_invalid_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            errors = doc_service.validate_file_upload("doc.exe", "application/x-executable", 1024)
            assert len(errors) > 0

    def test_validate_file_upload_oversized(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            errors = doc_service.validate_file_upload("doc.pdf", "application/pdf", 50 * 1024 * 1024)
            assert any("exceeds maximum" in e for e in errors)

    def test_validate_file_upload_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            errors = doc_service.validate_file_upload("doc.pdf", "application/pdf", 0)
            assert any("empty" in e for e in errors)

    def test_validate_file_upload_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            errors = doc_service.validate_file_upload("../../../etc/passwd", "application/pdf", 1024)
            assert any("path traversal" in e for e in errors)

    def test_validate_file_upload_blocked_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            errors = doc_service.validate_file_upload("malware.bat", "application/x-bat", 1024)
            assert any("blocked" in e for e in errors)

    @pytest.mark.asyncio
    async def test_store_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            result = await doc_service.store_document(
                file_content=b"test content",
                file_name="test.pdf",
                mime_type="application/pdf",
                user_id=str(uuid.uuid4()),
                document_type="identity_proof",
            )
            assert result["id"]
            assert result["status"] == "uploaded"

    @pytest.mark.asyncio
    async def test_process_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = FilesystemStorage(base_path=tmpdir)
            user_id = str(uuid.uuid4())
            ref = await storage.store(b"test aadhaar content", "aadhaar.pdf", "application/pdf", user_id)

            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), storage,
            )
            doc_id = str(uuid.uuid4())
            result = await doc_service.process_document(
                document_id=doc_id,
                user_id=user_id,
                storage_reference=ref,
                document_type="identity_proof",
                file_name="aadhaar.pdf",
            )
            assert result.document_id == doc_id
            assert result.confidence > 0
            assert len(result.extracted_fields) > 0

    @pytest.mark.asyncio
    async def test_verify_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            result = await doc_service.verify_document(
                document_id=str(uuid.uuid4()),
                user_id=str(uuid.uuid4()),
                verified_fields={"name": "Ravi Kumar", "date_of_birth": "2000-04-12"},
            )
            assert result["status"] == "verified"

    @pytest.mark.asyncio
    async def test_reject_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_service = DocumentService(
                MockOCRProvider(), DefaultDocumentExtractor(),
                DefaultDocumentValidator(), FilesystemStorage(tmpdir),
            )
            result = await doc_service.reject_document(
                document_id=str(uuid.uuid4()),
                user_id=str(uuid.uuid4()),
                reason="Document is blurry",
            )
            assert result["status"] == "rejected"
            assert result["reason"] == "Document is blurry"
