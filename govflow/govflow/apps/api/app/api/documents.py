import uuid
from typing import Any, Optional, List, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

router = APIRouter(prefix="/documents", tags=["documents"])

_documents_store: Dict[str, Dict[str, Any]] = {}


class DocumentUploadResponse(BaseModel):
    id: str
    user_id: str
    document_type: str
    file_name: str
    status: str
    message: str


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    document_type: str
    file_name: str
    storage_reference: str
    mime_type: str
    file_size: int
    verification_status: str
    ocr_status: str
    ocr_confidence: Optional[float] = None
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class DocumentProcessRequest(BaseModel):
    language: Optional[str] = Field(None, description="OCR language hint (en, kn, hi)")


class DocumentVerifyRequest(BaseModel):
    verified_fields: Dict[str, Any] = Field(..., description="User-verified field values")


class DocumentRejectRequest(BaseModel):
    reason: str = Field(..., description="Reason for rejection")


class DocumentRequirementsResponse(BaseModel):
    service_id: str
    operation: str
    requirements: List[Dict[str, Any]]


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    user_id: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a document for processing."""
    from packages.documents.document_service import DocumentService
    from packages.documents.ocr.mock_provider import MockOCRProvider
    from packages.documents.extraction.extractor import DefaultDocumentExtractor
    from packages.documents.validation.validator import DefaultDocumentValidator
    from packages.documents.storage.filesystem_storage import FilesystemStorage

    content = await file.read()

    ocr_provider = MockOCRProvider()
    extractor = DefaultDocumentExtractor()
    validator = DefaultDocumentValidator()
    storage = FilesystemStorage()

    doc_service = DocumentService(ocr_provider, extractor, validator, storage)

    errors = doc_service.validate_file_upload(
        file.filename or "unknown", file.content_type or "application/octet-stream", len(content)
    )
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    try:
        result = await doc_service.store_document(
            file_content=content,
            file_name=file.filename or "unknown",
            mime_type=file.content_type or "application/octet-stream",
            user_id=user_id,
            document_type=document_type,
        )
        _documents_store[result["id"]] = result
        return DocumentUploadResponse(
            id=result["id"],
            user_id=result["user_id"],
            document_type=result["document_type"],
            file_name=result["file_name"],
            status=result["status"],
            message="Document uploaded successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=DocumentListResponse)
async def list_documents(user_id: str, skip: int = 0, limit: int = 100):
    """List documents for a user."""
    user_docs = [d for d in _documents_store.values() if d["user_id"] == user_id]
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=d["id"], user_id=d["user_id"], document_type=d["document_type"],
                file_name=d["file_name"], storage_reference=d["storage_reference"],
                mime_type=d["mime_type"], file_size=d["file_size"],
                verification_status=d.get("verification_status", "pending"),
                ocr_status=d.get("ocr_status", "not_processed"),
                ocr_confidence=d.get("ocr_confidence"),
                extracted_data=d.get("extracted_data"),
                created_at=d.get("created_at", ""), updated_at=d.get("updated_at", ""),
            )
            for d in user_docs[skip:skip + limit]
        ],
        total=len(user_docs),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, user_id: str):
    """Get a specific document."""
    doc = _documents_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to document")
    return DocumentResponse(
        id=doc["id"], user_id=doc["user_id"], document_type=doc["document_type"],
        file_name=doc["file_name"], storage_reference=doc["storage_reference"],
        mime_type=doc["mime_type"], file_size=doc["file_size"],
        verification_status=doc.get("verification_status", "pending"),
        ocr_status=doc.get("ocr_status", "not_processed"),
        ocr_confidence=doc.get("ocr_confidence"),
        extracted_data=doc.get("extracted_data"),
        created_at=doc.get("created_at", ""), updated_at=doc.get("updated_at", ""),
    )


@router.post("/{document_id}/process")
async def process_document(document_id: str, request: DocumentProcessRequest):
    """Process a document through OCR and field extraction."""
    doc = _documents_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    from packages.documents.document_service import DocumentService
    from packages.documents.ocr.mock_provider import MockOCRProvider
    from packages.documents.extraction.extractor import DefaultDocumentExtractor
    from packages.documents.validation.validator import DefaultDocumentValidator
    from packages.documents.storage.filesystem_storage import FilesystemStorage

    ocr_provider = MockOCRProvider()
    extractor = DefaultDocumentExtractor()
    validator = DefaultDocumentValidator()
    storage = FilesystemStorage()

    doc_service = DocumentService(ocr_provider, extractor, validator, storage)

    result = await doc_service.process_document(
        document_id=document_id,
        user_id=doc["user_id"],
        storage_reference=doc["storage_reference"],
        document_type=doc["document_type"],
        file_name=doc["file_name"],
        language=request.language,
    )

    doc["ocr_status"] = result.status.value
    doc["ocr_confidence"] = result.confidence
    doc["extracted_data"] = {
        "fields": [
            {"field": f.field, "value": f.value, "confidence": f.confidence, "source": f.source.value}
            for f in result.extracted_fields
        ]
    }

    return {
        "document_id": document_id,
        "status": result.status.value,
        "confidence": result.confidence,
        "extracted_fields": len(result.extracted_fields),
        "validation_valid": result.validation_result.valid if result.validation_result else None,
    }


@router.post("/{document_id}/verify")
async def verify_document(document_id: str, request: DocumentVerifyRequest, user_id: str):
    """Verify a document after user review."""
    doc = _documents_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    from packages.documents.document_service import DocumentService
    from packages.documents.ocr.mock_provider import MockOCRProvider
    from packages.documents.extraction.extractor import DefaultDocumentExtractor
    from packages.documents.validation.validator import DefaultDocumentValidator
    from packages.documents.storage.filesystem_storage import FilesystemStorage

    doc_service = DocumentService(MockOCRProvider(), DefaultDocumentExtractor(), DefaultDocumentValidator(), FilesystemStorage())
    result = await doc_service.verify_document(document_id, user_id, request.verified_fields)
    doc["verification_status"] = "verified"
    return result


@router.post("/{document_id}/reject")
async def reject_document(document_id: str, request: DocumentRejectRequest, user_id: str):
    """Reject a document."""
    doc = _documents_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    from packages.documents.document_service import DocumentService
    from packages.documents.ocr.mock_provider import MockOCRProvider
    from packages.documents.extraction.extractor import DefaultDocumentExtractor
    from packages.documents.validation.validator import DefaultDocumentValidator
    from packages.documents.storage.filesystem_storage import FilesystemStorage

    doc_service = DocumentService(MockOCRProvider(), DefaultDocumentExtractor(), DefaultDocumentValidator(), FilesystemStorage())
    result = await doc_service.reject_document(document_id, user_id, request.reason)
    doc["verification_status"] = "rejected"
    return result
