import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class DocumentType(str):
    AADHAAR = "aadhaar"
    PAN = "pan"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    ADDRESS_PROOF = "address_proof"
    INCOME_PROOF = "income_proof"
    BIRTH_CERTIFICATE = "birth_certificate"
    PHOTOGRAPH = "photograph"
    OTHER = "other"


class DocumentStatus(str):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class OcrStatus(str):
    NOT_PROCESSED = "not_processed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type = Column(String(50), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    storage_reference = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    verification_status = Column(
        String(20), default=DocumentStatus.PENDING, nullable=False, index=True
    )
    ocr_status = Column(String(20), default=OcrStatus.NOT_PROCESSED, nullable=False)
    ocr_confidence = Column(Float, nullable=True)
    extracted_data = Column(JSONB, default=dict, nullable=True)
    extracted_data_ref = Column(String(500), nullable=True)
    metadata_extra = Column(JSONB, default=dict, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "document_type": self.document_type,
            "file_name": self.file_name,
            "storage_reference": self.storage_reference,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "verification_status": self.verification_status,
            "ocr_status": self.ocr_status,
            "ocr_confidence": self.ocr_confidence,
            "extracted_data": self.extracted_data,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
