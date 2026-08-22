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


class MockPassportRenewalAdapter(GovernmentServiceAdapter):
    """Mock adapter for Passport Renewal service.

    This is a test-only adapter for development and testing.
    It does NOT connect to any real government portal.
    """

    def metadata(self) -> ServiceMetadata:
        return ServiceMetadata(
            service_id="passport_renewal",
            display_name="Passport Renewal",
            description="Renewal of Indian passport through the Ministry of External Affairs",
            department="Ministry of External Affairs",
            jurisdiction="India",
            official_portal="https://www.passportindia.gov.in",
            supported_languages=["en", "kn", "hi"],
            capabilities=[
                ServiceCapability.DISCOVER,
                ServiceCapability.DOCUMENT_REQUIREMENTS,
                ServiceCapability.RENEW,
                ServiceCapability.TRACK_APPLICATION,
            ],
            required_documents=[
                DocumentRequirement(
                    document_type="current_passport",
                    display_name="Current Passport",
                    description="Original and photocopy of current passport",
                    mandatory=True,
                ),
                DocumentRequirement(
                    document_type="identity_proof",
                    display_name="Identity Proof",
                    description="Aadhaar Card or PAN Card",
                    mandatory=True,
                    examples=["Aadhaar Card", "PAN Card"],
                ),
                DocumentRequirement(
                    document_type="address_proof",
                    display_name="Address Proof",
                    description="Aadhaar Card, Utility Bill, or Rental Agreement",
                    mandatory=True,
                ),
                DocumentRequirement(
                    document_type="photograph",
                    display_name="Passport Size Photograph",
                    description="Recent passport size photograph with white background",
                    mandatory=True,
                ),
            ],
            aliases=[
                "passport renewal",
                "passport renew",
                "renew passport",
                "passport extension",
                "ಪಾಸ್‌ಪೋರ್ಟ್ ನವೀಕರಣ",
                "पासपोर्ट नवीनीकरण",
            ],
            workflow_version="2026.08",
            enabled=True,
            last_verified=datetime(2026, 8, 1),
            estimated_processing_time="30-45 working days",
            fees="₹1500 (normal) / ₹3500 (tatkal)",
            contact_info={
                "helpline": "1800-258-1811",
                "email": "help@passportindia.gov.in",
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

    async def track_application(self, reference_number: str) -> ServiceResponse:
        return ServiceResponse(
            success=True,
            data={
                "reference_number": reference_number,
                "status": "under_review",
                "current_step": "Police Verification Pending",
                "timeline": [
                    {"status": "submitted", "date": "2026-08-01", "note": "Application submitted"},
                    {"status": "under_review", "date": "2026-08-05", "note": "Documents verified"},
                    {"status": "police_verification", "date": "2026-08-10", "note": "Sent for police verification"},
                ],
                "estimated_completion": "2026-09-15",
            },
        )

    def _generate_workflow_steps(self, operation: str) -> List[WorkflowStep]:
        if operation == "renew":
            return [
                WorkflowStep(
                    id="verify_eligibility",
                    action="CHECK_ELIGIBILITY",
                    description="Verify passport expiry and eligibility for renewal",
                ),
                WorkflowStep(
                    id="collect_documents",
                    action="COLLECT_DOCUMENTS",
                    description="Collect current passport and supporting documents",
                ),
                WorkflowStep(
                    id="fill_form",
                    action="FILL_APPLICATION_FORM",
                    description="Fill the passport renewal application form online",
                    input_fields=["current_passport_number", "name", "address", "date_of_birth"],
                ),
                WorkflowStep(
                    id="upload_documents",
                    action="UPLOAD_DOCUMENTS",
                    description="Upload scanned copies of documents",
                ),
                WorkflowStep(
                    id="pay_fee",
                    action="PAY_APPLICATION_FEE",
                    description="Pay the passport renewal fee online",
                ),
                WorkflowStep(
                    id="schedule_appointment",
                    action="SCHEDULE_APPOINTMENT",
                    description="Schedule appointment at nearest Passport Seva Kendra",
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
                    description="Submit application at Passport Seva Kendra",
                    requires_human_approval=True,
                ),
            ]
        elif operation == "track_application":
            return [
                WorkflowStep(
                    id="enter_reference",
                    action="ENTER_REFERENCE_NUMBER",
                    description="Enter passport application reference number",
                    input_fields=["reference_number"],
                ),
                WorkflowStep(
                    id="fetch_status",
                    action="FETCH_STATUS",
                    description="Fetch current status from Passport Seva portal",
                ),
            ]
        return super()._generate_workflow_steps(operation)
