from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ServiceCapability(str, Enum):
    DISCOVER = "discover"
    ELIGIBILITY_CHECK = "eligibility_check"
    DOCUMENT_REQUIREMENTS = "document_requirements"
    NEW_APPLICATION = "new_application"
    UPDATE_RECORD = "update_record"
    RENEW = "renew"
    TRACK_APPLICATION = "track_application"
    RAISE_GRIEVANCE = "raise_grievance"


class DocumentRequirement(BaseModel):
    document_type: str
    display_name: str
    description: str
    mandatory: bool = True
    accepted_formats: List[str] = Field(default_factory=lambda: ["pdf", "jpg", "png"])
    max_file_size_mb: int = 5
    examples: List[str] = Field(default_factory=list)


class EligibilityCriteria(BaseModel):
    description: str
    criteria: List[str] = Field(default_factory=list)
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    residency_required: bool = True
    income_limit: Optional[float] = None
    additional_requirements: List[str] = Field(default_factory=list)


class WorkflowStep(BaseModel):
    id: str
    action: str
    description: str
    requires_human_approval: bool = False
    input_fields: List[str] = Field(default_factory=list)
    output_fields: List[str] = Field(default_factory=list)
    estimated_time_seconds: Optional[int] = None
    can_skip: bool = False


class ServiceMetadata(BaseModel):
    service_id: str
    display_name: str
    description: str
    department: str
    jurisdiction: str
    official_portal: str
    supported_languages: List[str] = Field(default_factory=lambda: ["en"])
    capabilities: List[ServiceCapability] = Field(default_factory=list)
    required_documents: List[DocumentRequirement] = Field(default_factory=list)
    workflow_version: str = "1.0.0"
    enabled: bool = True
    last_verified: Optional[datetime] = None
    estimated_processing_time: Optional[str] = None
    fees: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None


class ServiceError(BaseModel):
    error_code: str
    message: str
    recoverable: bool = True
    suggested_action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ServiceResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[ServiceError] = None


class CapabilityNotSupportedError(ServiceError):
    def __init__(self, capability: ServiceCapability, service_id: str):
        super().__init__(
            error_code="CAPABILITY_NOT_SUPPORTED",
            message=f"Capability '{capability.value}' is not supported by service '{service_id}'",
            recoverable=False,
            suggested_action="CHECK_CAPABILITIES",
        )