/**
 * In-memory mock data for the citizen dashboard.
 *
 * The dashboard reads from these mocks (via the `IRecentApplicationsApi`
 * interface) so the UI can be developed and tested without a live backend.
 */
import type { ApplicationStatus, IntentType } from "@govflow/shared";
import type {
  GovernmentTip,
  IRecentApplicationsApi,
  PopularService,
  RecentApplication,
} from "./api/types";

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  draft: "Draft",
  submitted: "Submitted",
  under_review: "Under Review",
  approved: "Approved",
  rejected: "Rejected",
  pending_action: "Action Required",
  expired: "Expired",
};

/** Intent chips rendered below the AI prompt box. */
export const PROMPT_INTENT_OPTIONS: Array<{ value: IntentType; label: string }> =
  [
    { value: "NEW_APPLICATION", label: "Apply" },
    { value: "UPDATE_RECORD", label: "Update" },
    { value: "TRACK_APPLICATION", label: "Track" },
    { value: "RAISE_GRIEVANCE", label: "Complaint" },
  ];

export const mockRecentApplications: RecentApplication[] = [
  {
    id: "app_01",
    serviceId: "svc_income",
    service: "Income Certificate",
    status: "under_review",
    date: "2024-08-12T10:30:00Z",
    referenceNumber: "INC/2024/001847",
    nextAction: "Upload remaining income proof",
  },
  {
    id: "app_02",
    serviceId: "svc_driving",
    service: "Driving License (Renewal)",
    status: "approved",
    date: "2024-08-05T09:15:00Z",
    referenceNumber: "DL/REN/2024/033210",
  },
  {
    id: "app_03",
    serviceId: "svc_caste",
    service: "Caste Certificate",
    status: "pending_action",
    date: "2024-07-28T14:20:00Z",
    referenceNumber: "CASTE/2024/009521",
    nextAction: "Confirm appointment slot",
  },
];

export const mockPopularServices: PopularService[] = [
  {
    id: "svc_income",
    name: "Income Certificate",
    category: "Revenue",
    icon: "📄",
    href: "/apply?service=svc_income",
  },
  {
    id: "svc_driving",
    name: "Driving License",
    category: "Transport",
    icon: "🚗",
    href: "/apply?service=svc_driving",
  },
  {
    id: "svc_birth",
    name: "Birth Certificate",
    category: "Civil Registration",
    icon: "📜",
    href: "/apply?service=svc_birth",
  },
  {
    id: "svc_aadhaar",
    name: "Aadhaar Update",
    category: "Identity",
    icon: "🆔",
    href: "/apply?service=svc_aadhaar",
  },
  {
    id: "svc_pension",
    name: "Senior Citizen Pension",
    category: "Social Welfare",
    icon: "👴",
    href: "/apply?service=svc_pension",
  },
  {
    id: "svc_property",
    name: "Property Tax Payment",
    category: "Municipal",
    icon: "🏠",
    href: "/apply?service=svc_property",
  },
];

export const mockGovernmentTips: GovernmentTip[] = [
  {
    id: "tip_01",
    icon: "📎",
    title: "Gather documents first",
    description:
      "Have your Aadhaar, PAN and proof of address ready before starting any application.",
  },
  {
    id: "tip_02",
    icon: "🔢",
    title: "Keep reference numbers safe",
    description:
      "Every application gets a unique reference number. Use it to track status online at any time.",
  },
  {
    id: "tip_03",
    icon: "🛡️",
    title: "Verify official portals",
    description:
      "GovFlow always navigates to the official .gov domain. Check the URL bar before entering personal data.",
  },
  {
    id: "tip_04",
    icon: "⏰",
    title: "Apply during business hours",
    description:
      "Submission success rates are higher between 9 AM and 5 PM on weekdays.",
  },
];

/** Mock implementation of `IRecentApplicationsApi` — resolves from memory. */
export const mockRecentApplicationsApi: IRecentApplicationsApi = {
  async getRecentApplications(_userId: string) {
    return new Promise<RecentApplication[]>((resolve) =>
      setTimeout(() => resolve(mockRecentApplications), 300)
    );
  },
};

// ---------------------------------------------------------------------------
// Document Vault Mock Data
// ---------------------------------------------------------------------------

import type {
  VaultDocument,
  UploadConfig,
  ApprovalRequest,
  ApprovalResult,
  GrievanceTicket,
  GrievanceSubmitResult,
} from "./api/types";

export const UPLOAD_CONFIG: UploadConfig = {
  maxFileSizeMB: 10,
  acceptedTypes: ["application/pdf", "image/png", "image/jpeg"],
};

export const mockDocuments: VaultDocument[] = [
  {
    id: "doc_01",
    name: "Aadhaar Card.pdf",
    type: "pdf",
    category: "Identity",
    size: 2_516_582,
    status: "verified",
    uploadedAt: "2024-08-10T09:00:00Z",
    extractedData: {
      name: "Rajesh Kumar",
      dateOfBirth: "1990-05-14",
      address: "42 MG Road, Bengaluru, Karnataka 560001",
      documentType: "Aadhaar Card",
    },
  },
  {
    id: "doc_02",
    name: "Income Certificate.pdf",
    type: "pdf",
    category: "Revenue",
    size: 1_258_291,
    status: "verified",
    uploadedAt: "2024-08-05T14:30:00Z",
    extractedData: {
      name: "Rajesh Kumar",
      dateOfBirth: "1990-05-14",
      address: "42 MG Road, Bengaluru, Karnataka 560001",
      documentType: "Income Certificate",
    },
  },
  {
    id: "doc_03",
    name: "Address Proof.jpg",
    type: "jpg",
    category: "Address",
    size: 3_984_512,
    status: "needs_review",
    uploadedAt: "2024-08-01T11:15:00Z",
  },
  {
    id: "doc_04",
    name: "Driving License.pdf",
    type: "pdf",
    category: "Transport",
    size: 1_887_436,
    status: "verified",
    uploadedAt: "2024-07-28T08:45:00Z",
    extractedData: {
      name: "Rajesh Kumar",
      dateOfBirth: "1990-05-14",
      address: "42 MG Road, Bengaluru, Karnataka 560001",
      documentType: "Driving License",
    },
  },
  {
    id: "doc_05",
    name: " PAN Card.png",
    type: "png",
    category: "Identity",
    size: 524_288,
    status: "processing",
    uploadedAt: "2024-07-25T16:00:00Z",
  },
  {
    id: "doc_06",
    name: "Property Tax Receipt.pdf",
    type: "pdf",
    category: "Property",
    size: 2_097_152,
    status: "rejected",
    uploadedAt: "2024-07-20T10:30:00Z",
  },
];

// ---------------------------------------------------------------------------
// Human Approval Mock Data
// ---------------------------------------------------------------------------

export const mockApprovalRequest: ApprovalRequest = {
  id: "apr_001",
  service: "Income Certificate",
  serviceDescription:
    "Application for issuance of Income Certificate for the financial year 2024-25, required for scholarship admission at Bengaluru University.",
  department: {
    name: "Revenue Department",
    code: "REV",
    jurisdiction: "Bengaluru Urban",
    contactEmail: "revenue@karnataka.gov.in",
    contactPhone: "080-2221-1234",
  },
  portal: {
    name: "Karnataka e-Service Portal",
    url: "https://eservices.karnataka.gov.in",
    lastVerified: "2024-08-10T00:00:00Z",
  },
  applicant: {
    name: "Rajesh Kumar",
    dateOfBirth: "1990-05-14",
    gender: "Male",
    email: "rajesh.kumar@email.com",
    phone: "+91 98765 43210",
    address: "42 MG Road, Bengaluru, Karnataka 560001",
    aadhaarLast4: "7890",
  },
  documents: [
    {
      id: "doc_01",
      name: "Aadhaar Card.pdf",
      type: "PDF",
      size: 2_516_582,
      status: "verified",
    },
    {
      id: "doc_02",
      name: "Income Certificate.pdf",
      type: "PDF",
      size: 1_258_291,
      status: "verified",
    },
    {
      id: "doc_03",
      name: "Address Proof.jpg",
      type: "JPEG",
      size: 3_984_512,
      status: "needs_review",
    },
  ],
  formFields: [
    { label: "Applicant Name", value: "Rajesh Kumar" },
    { label: "Father's Name", value: "Suresh Kumar" },
    { label: "Annual Income", value: "₹3,60,000" },
    { label: "Income Source", value: "Salaried" },
    { label: "Purpose", value: "Scholarship Admission" },
    { label: "Institution", value: "Bengaluru University" },
    { label: "Certificate Validity", value: "1 Year" },
    { label: "Delivery Method", value: "Online (DigiLocker)" },
  ],
  createdAt: "2024-08-12T10:30:00Z",
};

/** Placeholder mutation — simulates an API call to submit the approval. */
export async function submitApproval(
  _requestId: string
): Promise<ApprovalResult> {
  return new Promise((resolve) =>
    setTimeout(() => {
      resolve({
        referenceNumber: `REV/2024/${String(Math.floor(Math.random() * 999999)).padStart(6, "0")}`,
        submittedAt: new Date().toISOString(),
        nextSteps: [
          "Your application has been submitted to the Revenue Department.",
          "You will receive an SMS confirmation within 24 hours.",
          "The certificate will be available in DigiLocker within 3-5 business days.",
          "For queries, contact the helpdesk at 1800-110-001