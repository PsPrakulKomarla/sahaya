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


class MockIncomeCertificateAdapter(GovernmentServiceAdapter):
    """Mock adapter for Income Certificate service.

    This is a test-only adapter for development and testing.
    It does NOT connect to any real government portal.
    """

    def metadata(self) -> ServiceMetadata:
        return ServiceMetadata(
            service_id="income_certificate",
            display_name="Income Certificate",
            description="Official document certifying an individual's income from all sources",
            department="Revenue Department",
            jurisdiction="Karnataka",
            official_portal="https://karnataka.gov.in",
            supported_languages=["en", "kn", "hi"],
            capabilities=[
                ServiceCapability.DISCOVER,
                ServiceCapability.ELIGIBILITY_CHECK,
                ServiceCapability.DOCUMENT_REQUIREMENTS,
                ServiceCapability.NEW_APPLICATION,
                ServiceCapability.TRACK_APPLICATION,
                ServiceCapability.RAISE_GRIEVANCE,
            ],
            required_documents=[
                DocumentRequirement(
                    document_type="identity_proof",
                    display_name="Identity Proof",
                    description="Aadhaar Card, PAN Card, or Voter ID",
                    mandatory=True,
                    examples=["Aadhaar Card", "PAN Card", "Voter ID"],
                ),
                DocumentRequirement(
                    document_type="address_proof",
                    display_name="Address Proof",
                    description="Aadhaar Card, Utility Bill, or Rental Agreement",
                    mandatory=True,
                    examples=["Aadhaar Card", "Electricity Bill", "Rental Agreement"],
                ),
                DocumentRequirement(
                    document_type="income_proof",
                    display_name="Income Proof",
                    description="Salary slip, Form 16, or Income Declaration",
                    mandatory=True,
                    examples=["Salary Slip", "Form 16", "Income Declaration"],
                ),
                DocumentRequirement(
                    document_type="photograph",
                    display_name="Passport Size Photograph",
                    description="Recent passport size photograph",
                    mandatory=True,
                ),
            ],
            workflow_version="2026.08",
            enabled=True,
            last_verified=datetime(2026, 8, 1),
            estimated_processing_time="7-10 working days",
            fees="₹25 (application fee)",
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
        age = user_data.get("age")
        income = user_data.get("annual_income")
        residency = user_data.get("is_resident", False)

        criteria = []
        eligible = True

        if age is not None and age < 18:
            criteria.append("Applicant must be at least 18 years old")
            eligible = False

        if not residency:
            criteria.append("Applicant must be a resident of Karnataka")
            eligible = False

        if income is not None and income > 1000000:
            criteria.append("Annual income must be below ₹10,00,000")
            eligible = False

        return ServiceResponse(
            success=True,
            data={
                "eligible": eligible,
                "criteria": criteria,
                "notes": [
                    "Income certificate is valid for 6 months from date of issue",
                    "Processing time: 7-10 working days",
                ],
            },
        )

    async def create_application(self, application_data: Dict[str, Any]) -> ServiceResponse:
        required_fields = ["full_name", "father_name", "address", "income"]
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
                "application_id": "MOCK-IC-2026-001",
                "reference_number": "MOCK-REF-2026-001",
                "status": "submitted",
                "message": "Application submitted successfully (MOCK)",
            },
        )

    async def track_application(self, reference_number: str) -> ServiceResponse:
        return ServiceResponse(
            success=True,
            data={
                "reference_number": reference_number,
                "status": "under_review",
                "current_step": "Verification by Revenue Officer",
                "timeline": [
                    {"status": "submitted", "date": "2026-08-01", "note": "Application submitted"},
                    {"status": "under_review", "date": "2026-08-03", "note": "Sent for verification"},
                ],
                "estimated_completion": "2026-08-15",
            },
        )

    async def create_grievance(self, grievance_data: Dict[str, Any]) -> ServiceResponse:
        return ServiceResponse(
            success=True,
            data={
                "grievance_id": "MOCK-GRIEV-2026-001",
                "status": "submitted",
                "message": "Grievance registered successfully (MOCK)",
            },
        )

    def _generate_workflow_steps(self, operation: str) -> List[WorkflowStep]:
        if operation == "new_application":
            return [
                WorkflowStep(
                    id="verify_eligibility",
                    action="CHECK_ELIGIBILITY",
                    description="Verify applicant eligibility",
                ),
                WorkflowStep(
                    id="collect_documents",
                    action="COLLECT_DOCUMENTS",
                    description="Collect and verify required documents",
                ),
                WorkflowStep(
                    id="fill_form",
                    action="FILL_APPLICATION_FORM",
                    description="Fill the income certificate application form",
                    input_fields=["full_name", "father_name", "address", "income", "purpose"],
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
                WorkflowStep(
                    id="track",
                    action="TRACK_APPLICATION",
                    description="Track application status",
                ),
            ]
        elif operation == "track_application":
            return [
                WorkflowStep(
                    id="enter_reference",
                    action="ENTER_REFERENCE_NUMBER",
                    description="Enter application reference number",
                    input_fields=["reference_number"],
                ),
                WorkflowStep(
                    id="fetch_status",
                    action="FETCH_STATUS",
                    description="Fetch current status from portal",
                ),
            ]
        return super()._generate_workflow_steps(operation)