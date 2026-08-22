from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentType(str, Enum):
    IDENTITY_PROOF = "identity_proof"
    ADDRESS_PROOF = "address_proof"
    INCOME_PROOF = "income_proof"
    BIRTH_CERTIFICATE = "birth_certificate"
    PASSPORT = "passport"
    DRIVING_LICENCE = "driving_licence"
    EDUCATION_CERTIFICATE = "education_certificate"
    BANK_DOCUMENT = "bank_document"
    PHOTOGRAPH = "photograph"
    HOSPITAL_RECORD = "hospital_record"
    PARENTS_ID = "parents_id"
    AFFIDAVIT = "affidavit"
    OTHER = "other"


class DocumentPipelineStatus(str, Enum):
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    OCR_PROCESSING = "ocr_processing"
    EXTRACTING = "extracting"
    NEEDS_REVIEW = "needs_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    FAILED = "failed"


class FieldSource(str, Enum):
    OCR = "ocr"
    USER_PROVIDED = "user_provided"
    VERIFIED = "verified"
    EXTERNAL_VERIFICATION = "external_verification"


class ExpiryStatus(str, Enum):
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class ExtractedField(BaseModel):
    field: str
    value: Any
    confidence: float = 0.0
    source: FieldSource = FieldSource.OCR
    ocr_value: Optional[str] = None
    verified: bool = False
    verified_at: Optional[datetime] = None


class OCRBoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float
    text: str
    confidence: float


class OCRPageResult(BaseModel):
    page_number: int
    text: str
    confidence: float
    bounding_boxes: List[OCRBoundingBox] = Field(default_factory=list)
    language: Optional[str] = None


class OCRResult(BaseModel):
    extracted_text: str
    pages: List[OCRPageResult] = Field(default_factory=list)
    overall_confidence: float = 0.0
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentValidationResult(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    field_formats: Dict[str, bool] = Field(default_factory=dict)


class DocumentAvailabilityResult(BaseModel):
    required_type: str
    display_name: str
    mandatory: bool
    available: bool
    matching_documents: List[str] = Field(default_factory=list)
    expiry_status: ExpiryStatus = ExpiryStatus.UNKNOWN


class DocumentRequirementItem(BaseModel):
    document_type: str
    display_name: str
    description: str = ""
    mandatory: bool = True
    accepted_formats: List[str] = Field(default_factory=lambda: ["pdf", "jpg", "png"])
    max_file_size_mb: int = 5


class RequiredDocumentsResult(BaseModel):
    service_id: str
    operation: str
    requirements: List[DocumentRequirementItem] = Field(default_factory=list)


class DocumentMatchResult(BaseModel):
    required_type: str
    matched: bool
    document_id: Optional[str] = None
    document_type: Optional[str] = None
    confidence: float = 0.0
    expiry_status: ExpiryStatus = ExpiryStatus.UNKNOWN


class CrossDocumentCheckResult(BaseModel):
    consistent: bool
    discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    checked_fields: List[str] = Field(default_factory=list)


class DocumentProcessingResult(BaseModel):
    document_id: str
    status: DocumentPipelineStatus
    ocr_result: Optional[OCRResult] = None
    extracted_fields: List[ExtractedField] = Field(default_factory=list)
    validation_result: Optional[DocumentValidationResult] = None
    confidence: float = 0.0
    errors: List[str] = Field(default_factory=list)
