/**
 * Mock API surface for the citizen dashboard.
 *
 * These are plain TypeScript interfaces + in-memory mock data. No HTTP client
 * or real network calls are involved. When the backend API is ready, swap the
 * mock implementation in `lib/mock-data.ts` for a real one that implements the
 * `IRecentApplicationsApi` interface below.
 */
import type { ApplicationStatus, IntentType } from "@govflow/shared";

/** A citizen-facing view of an application. */
export interface RecentApplication {
  id: string;
  service: string;
  serviceId: string;
  status: ApplicationStatus;
  /** ISO 8601 date string the application was created / last updated. */
  date: string;
  referenceNumber?: string;
  /** Suggested next step shown to the citizen. */
  nextAction?: string;
}

/** A service card shown on the dashboard. */
export interface PopularService {
  id: string;
  name: string;
  category: string;
  icon: string;
  href?: string;
}

/** A tip surfaced from a government source. */
export interface GovernmentTip {
  id: string;
  title: string;
  description: string;
  icon?: string;
}

/** Payload sent to the agent. */
export interface AgentRequest {
  input: string;
  intent: IntentType;
}

/** Result returned from the agent. Intentionally a stub (see `useAgent`). */
export interface AgentResponse {
  ok: boolean;
  intent: IntentType;
  input: string;
  /** Placeholder: real AI content is wired up in a later phase. */
  content?: string;
}

/** Contract for any data source that provides recent applications. */
export interface IRecentApplicationsApi {
  getRecentApplications(userId: string): Promise<RecentApplication[]>;
}

export type { ApplicationStatus, IntentType };

/** Document upload status in the vault. */
export type DocumentStatus =
  | "processing"
  | "verified"
  | "needs_review"
  | "rejected";

/** A document stored in the citizen's vault. */
export interface VaultDocument {
  id: string;
  name: string;
  type: "pdf" | "png" | "jpg" | "jpeg";
  category: string;
  size: number;
  status: DocumentStatus;
  uploadedAt: string;
  extractedData?: OcrData;
}

/** OCR-extracted fields from a scanned document. */
export interface OcrData {
  name: string;
  dateOfBirth: string;
  address: string;
  documentType: string;
}

/** Configurable upload constraints. */
export interface UploadConfig {
  maxFileSizeMB: number;
  acceptedTypes: string[];
}

// ---------------------------------------------------------------------------
// Human Approval
// ---------------------------------------------------------------------------

/** Department metadata shown on the approval review page. */
export interface DepartmentInfo {
  name: string;
  code: string;
  jurisdiction: string;
  contactEmail: string;
  contactPhone: string;
}

/** Official government portal the submission targets. */
export interface PortalInfo {
  name: string;
  url: string;
  lastVerified: string;
}

/** Applicant details for the approval review. */
export interface ApplicantInfo {
  name: string;
  dateOfBirth: string;
  gender: string;
  email: string;
  phone: string;
  address: string;
  aadhaarLast4: string;
}

/** A document attachment on the approval request. */
export interface ApprovalDocument {
  id: string;
  name: string;
  type: string;
  size: number;
  status: "verified" | "needs_review" | "rejected";
}

/** Key-value row in the form summary. */
export interface FormField {
  label: string;
  value: string;
}

/** Full approval request payload displayed on the review page. */
export interface ApprovalRequest {
  id: string;
  service: string;
  serviceDescription: string;
  department: DepartmentInfo;
  portal: PortalInfo;
  applicant: ApplicantInfo;
  documents: ApprovalDocument[];
  formFields: FormField[];
  createdAt: string;
}

/** Result returned after a successful approval submission. */
export interface ApprovalResult {
  referenceNumber: string;
  submittedAt: string;
  nextSteps: string[];
}

// ---------------------------------------------------------------------------
// Grievance Center
// ---------------------------------------------------------------------------

/** Categories of grievance a citizen can file. */
export type GrievanceCategory =
  | "delay"
  | "incorrect_info"
  | "missing_update"
  | "technical_issue"
  | "other";

export const GRIEVANCE_CATEGORY_LABELS: Record<GrievanceCategory, string> = {
  delay: "Delay",
  incorrect_info: "Incorrect Information",
  missing_update: "Missing Update",
  technical_issue: "Technical Issue",
  other: "Other",
};

/** Status of a submitted grievance ticket. */
export type GrievanceTicketStatus =
  | "submitted"
  | "under_review"
  | "in_progress"
  | "resolved"
  | "closed";

export const GRIEVANCE_STATUS_LABELS: Record<GrievanceTicketStatus, string> = {
  submitted: "Submitted",
  under_review: "Under Review",
  in_progress: "In Progress",
  resolved: "Resolved",
  closed: "Closed",
};

/** A grievance ticket submitted by the citizen. */
export interface GrievanceTicket {
  id: string;
  applicationId: string;
  applicationService: string;
  referenceNumber: string;
  category: GrievanceCategory;
  description: string;
  department: string;
  status: GrievanceTicketStatus;
  createdAt: string;
  updatedAt: string;
  attachments: GrievanceAttachment[];
}

/** Attachment on a grievance. */
export interface GrievanceAttachment {
  id: string;
  name: string;
  size: number;
  type: string;
}

/** The complaint form draft before submission. */
export interface GrievanceDraft {
  applicationId: string;
  category: GrievanceCategory | "";
  description: string;
  attachments: File[];
}

/** Result returned after a successful grievance submission. */
export interface GrievanceSubmitResult {
  ticketId: string;
  submittedAt: string;
  message: string;
}