from typing import Optional, Dict, Any, List
from datetime import datetime
from packages.services.base.adapter import GovernmentServiceAdapter
from packages.services.base.models import (
    ServiceMetadata,
    ServiceCapability,
    ServiceResponse,
    DocumentRequirement,
    WorkflowStep,
)


class MockBirthCertificateAdapter(GovernmentServiceAdapter):
    """Mock adapter for Birth Certificate service.

    This is a test-only adapter for development and testing.
    It does NOT connect to any real government portal.
    """

    def metadata(self) -> ServiceMetadata:
        return ServiceMetadata(
            service_id="birth_certificate",
            display_name="Birth Certificate",
            description="Official document certifying the birth of a person",
            department="Department of Health and Family Welfare",
            jurisdiction="Karnataka",
            official_portal="https://karnataka.gov.in",
            supported_languages=["en", "kn", "hi"],
            capabilities=[
                ServiceCapability.DISCOVER,
                ServiceCapability.DOCUMENT_REQUIREMENTS,
                ServiceCapability.NEW_APPLICATION,
                ServiceCapability.TRACK_APPLICATION,
            ],
            required_documents=[
                DocumentRequirement(
                    document_type="hospital_record",
                    display_name="Hospital Birth Record",
                    description="Official record from the hospital where birth occurred",
                    mandatory=True,
                ),
                DocumentRequirement(
                    document_type="parents_id",
                    display_name="Parents' Identity Proof",
                    description="Aadhaar Card or PAN Card of parents",
                    mandatory=True,
                    examples=["Aadhaar Card", "PAN Card"],
                ),
                DocumentRequirement(
                    document_type="address_proof",
                    display_name="Address Proof",
                    description="Current address proof of parents",
                    mandatory=True,
                ),
                DocumentRequirement(
                    document_type="affidavit",
                    display_name="Affidavit",
                    description="Affidavit declaring the birth details",
                    mandatory=False,
                ),
            ],
            aliases=[
                "birth certificate",
                "birth cert",
                "birth proof",
                "birth registration",
                "ಜನನ ಪ್ರಮಾಣಪತ್ರ",
                "जन्म प्रमाण पत्र",
            ],
            workflow_version="2026.08",
            enabled=True,
            last_verified=datetime(2026, 8, 1),
            estimated_processing_time="15-20 working days",
            fees="₹10 (application fee)",
            contact_info={
                "helpline": "1800-XXX-XXXX",
                "email": "help@karnataka.gov.in",
            },
        )

    async def discover(self, query: str, jurisdiction: Optional[str] = None) -> ServiceResponse:
        metadata = self.metadata()
        return ServiceResponse(
            success=True,
            data={
                "service_id": metadata.service_id,
                "display_name": metadata.display_name,
                "description": metadata.description,
                "department": metadata.department,
                "jurisdiction": metadata.jurisdiction,
                "official_portal": metadata.official_portal,
                "capabilities": [c.value for c in metadata.capabilities],
            },
        )

    async def check_eligibility(self, user_data: Dict[str, Any]) -> ServiceResponse:
        birth_date = user_data.get("birth_date")
        birth_place = user_data.get("birth_place")

        criteria = []
        eligible = True

        if not birth_date:
            criteria.append("Birth date is required")
            eligible = False

        if not birth_place:
            criteria.append("Birth place is required")
            eligible = False

        return ServiceResponse(
            success=True,
            data={
                "eligible": eligible,
                "criteria": criteria,
                "notes": [
                    "Birth certificate can be applied within 21 days of birth",
                    "Late registration requires additional documentation",
                ],
            },
        )

    async def create_application(self, application_data: Dict[str, Any]) -> ServiceResponse:
        required_fields = ["child_name", "birth_date", "birth_place", "parents_names"]
        missing = [f for f in required_fields if f not in application_data]

        if missing:
            return ServiceResponse(
                success=False,
                error={
                    "error_code": "MISSING_FIELDS",
                    "message": f"Required fields missing: {', '.join(missing)}",
                    "recoverable": True,
                    "suggested_action": "PROVIDE_MISSING_FIELDS",
                },
            )

        return ServiceResponse(
            success=True,
            data={
                "application_id": "MOCK-BC-2026-001",
                "reference_number": "MOCK-REF-BC-2026-001",
                "status": "submitted",
                "message": "Birth certificate application submitted successfully (MOCK)",
            },
        )

    async def track_application(self, reference_number: str) -> ServiceResponse:
        return ServiceResponse(
            success=True,
            data={
                "reference_number": reference_number,
                "status": "under_review",
                "current_step": "Verification by Health Officer",
                "timeline": [
                    {"status": "submitted", "date": "2026-08-01", "note": "Application submitted"},
                    {"status": "under_review", "date": "2026-08-05", "note": "Sent for hospital verification"},
                ],
                "estimated_completion": "2026-08-20",
            },
        )

    def _generate_workflow_steps(self, operation: str) -> List[WorkflowStep]:
        if operation == "new_application":
            return [
                WorkflowStep(
                    id="verify_eligibility",
                    action="CHECK_ELIGIBILITY",
                    description="Verify birth details and eligibility",
                ),
                WorkflowStep(
                    id="collect_documents",
                    action="COLLECT_DOCUMENTS",
                    description="Collect hospital records and parent IDs",
                ),
                WorkflowStep(
                    id="fill_form",
                    action="FILL_APPLICATION_FORM",
                    description="Fill the birth certificate application form",
                    input_fields=["child_name", "birth_date", "birth_place", "parents_names", "address"],
                ),
                WorkflowStep(
                    id="upload_documents",
                    action="UPLOAD_DOCUMENTS",
                    description="Upload supporting documents",
                ),
                WorkflowStep(
                    id="review",
                    action="HUMAN_REVIEW",
                    description="Review application before submission",
                    requires_human_approval=True,
                ),
                WorkflowStep(
                    id="submit",
                    action="SUBMIT_APPLICATION",
                    description="Submit application to government portal",
                    requires_human_approval=True,
                ),
            ]
        return super()._generate_workflow_steps(operation)