import { z } from "zod";

export const SupportedLanguageSchema = z.enum(["en", "kn", "hi"]);
export type SupportedLanguage = z.infer<typeof SupportedLanguageSchema>;

export const ServiceCapabilitySchema = z.enum([
  "apply",
  "update",
  "track",
  "grievance",
  "check_documents",
  "check_eligibility",
]);
export type ServiceCapability = z.infer<typeof ServiceCapabilitySchema>;

export const IntentTypeSchema = z.enum([
  "NEW_APPLICATION",
  "UPDATE_RECORD",
  "TRACK_APPLICATION",
  "RAISE_GRIEVANCE",
  "CHECK_DOCUMENTS",
  "CHECK_ELIGIBILITY",
  "UNKNOWN",
]);
export type IntentType = z.infer<typeof IntentTypeSchema>;

export const AgentStateSchema = z.enum([
  "DISCOVER",
  "VERIFY_SOURCE",
  "UNDERSTAND_REQUIREMENTS",
  "CHECK_ELIGIBILITY",
  "REQUEST_DOCUMENTS",
  "VALIDATE_DOCUMENTS",
  "PLAN",
  "EXECUTE",
  "VERIFY_RESULT",
  "HUMAN_APPROVAL",
  "SUBMIT",
  "TRACK",
  "COMPLETE",
  "ERROR",
  "RECOVER",
  "HUMAN_REVIEW",
]);
export type AgentState = z.infer<typeof AgentStateSchema>;

export const DocumentTypeSchema = z.enum([
  "aadhaar",
  "pan",
  "passport",
  "driving_license",
  "utility_bill",
  "birth_certificate",
  "income_proof",
  "residence_proof",
  "other",
]);
export type DocumentType = z.infer<typeof DocumentTypeSchema>;

export const DocumentVerificationStatusSchema = z.enum([
  "pending",
  "verified",
  "rejected",
  "needs_review",
]);
export type DocumentVerificationStatus = z.infer<typeof DocumentVerificationStatusSchema>;

export const ApplicationStatusSchema = z.enum([
  "draft",
  "submitted",
  "under_review",
  "approved",
  "rejected",
  "pending_action",
  "expired",
]);
export type ApplicationStatus = z.infer<typeof ApplicationStatusSchema>;

export const GrievanceStatusSchema = z.enum([
  "draft",
  "submitted",
  "under_review",
  "resolved",
  "rejected",
]);
export type GrievanceStatus = z.infer<typeof GrievanceStatusSchema>;

export const ServiceSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  jurisdiction: z.string(),
  department: z.string(),
  officialPortal: z.string().url(),
  capabilities: z.array(ServiceCapabilitySchema),
  requiredDocuments: z.array(DocumentTypeSchema),
  adapter: z.string(),
  workflowVersion: z.string(),
  lastVerified: z.string().datetime(),
  isActive: z.boolean().default(true),
});
export type Service = z.infer<typeof ServiceSchema>;

export const DocumentSchema = z.object({
  id: z.string(),
  userId: z.string(),
  type: DocumentTypeSchema,
  fileName: z.string(),
  filePath: z.string(),
  mimeType: z.string(),
  fileSize: z.number(),
  extractedData: z.record(z.unknown()).optional(),
  verificationStatus: DocumentVerificationStatusSchema,
  confidence: z.number().min(0).max(1).optional(),
  verifiedAt: z.string().datetime().optional(),
  expiresAt: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type Document = z.infer<typeof DocumentSchema>;

export const ApplicationSchema = z.object({
  id: z.string(),
  userId: z.string(),
  serviceId: z.string(),
  referenceNumber: z.string().optional(),
  status: ApplicationStatusSchema,
  formData: z.record(z.unknown()),
  documents: z.array(z.string()),
  submittedAt: z.string().datetime().optional(),
  lastCheckedAt: z.string().datetime().optional(),
  timeline: z.array(
    z.object({
      status: ApplicationStatusSchema,
      timestamp: z.string().datetime(),
      note: z.string().optional(),
    })
  ),
  nextAction: z.string().optional(),
  grievanceId: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type Application = z.infer<typeof ApplicationSchema>;

export const GrievanceSchema = z.object({
  id: z.string(),
  userId: z.string(),
  applicationId: z.string().optional(),
  serviceId: z.string(),
  title: z.string(),
  description: z.string(),
  referenceNumber: z.string().optional(),
  status: GrievanceStatusSchema,
  submittedAt: z.string().datetime().optional(),
  resolvedAt: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type Grievance = z.infer<typeof GrievanceSchema>;

export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email().optional(),
  phone: z.string().optional(),
  preferredLanguage: SupportedLanguageSchema.default("en"),
  profile: z
    .object({
      name: z.string().optional(),
      dateOfBirth: z.string().optional(),
      address: z.string().optional(),
    })
    .optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type User = z.infer<typeof UserSchema>;

export const AgentRunSchema = z.object({
  id: z.string(),
  userId: z.string(),
  intent: IntentTypeSchema,
  serviceId: z.string().optional(),
  portal: z.string().optional(),
  currentState: AgentStateSchema,
  actions: z.array(
    z.object({
      type: z.string(),
      description: z.string(),
      timestamp: z.string().datetime(),
      success: z.boolean(),
      error: z.string().optional(),
      metadata: z.record(z.unknown()).optional(),
    })
  ),
  errors: z.array(
    z.object({
      code: z.string(),
      message: z.string(),
      timestamp: z.string().datetime(),
      recovered: z.boolean().default(false),
    })
  ),
  recoveryAttempts: z.number().default(0),
  humanApprovals: z.array(
    z.object({
      action: z.string(),
      approved: z.boolean(),
      timestamp: z.string().datetime(),
    })
  ),
  finalResult: z
    .object({
      success: z.boolean(),
      referenceNumber: z.string().optional(),
      applicationId: z.string().optional(),
      grievanceId: z.string().optional(),
      error: z.string().optional(),
    })
    .optional(),
  startedAt: z.string().datetime(),
  completedAt: z.string().datetime().optional(),
});
export type AgentRun = z.infer<typeof AgentRunSchema>;

export const StructuredIntentSchema = z.object({
  intent: IntentTypeSchema,
  service: z.string().optional(),
  jurisdiction: z.string().optional(),
  portal: z.string().optional(),
  requirements: z.array(z.string()).optional(),
  missingDocuments: z.array(DocumentTypeSchema).optional(),
  nextAction: AgentStateSchema,
  confidence: z.number().min(0).max(1),
  rawInput: z.string(),
  language: SupportedLanguageSchema,
});
export type StructuredIntent = z.infer<typeof StructuredIntentSchema>;

export const BrowserActionSchema = z.object({
  type: z.enum([
    "navigate",
    "click",
    "fill",
    "select",
    "upload",
    "extract",
    "wait",
    "scroll",
    "screenshot",
  ]),
  selector: z.string().optional(),
  value: z.string().optional(),
  url: z.string().optional(),
  description: z.string(),
  confidence: z.number().min(0).max(1),
  alternatives: z
    .array(
      z.object({
        selector: z.string(),
        confidence: z.number().min(0).max(1),
        reason: z.string(),
      })
    )
    .optional(),
});
export type BrowserAction = z.infer<typeof BrowserActionSchema>;

export const WorkflowStepSchema = z.object({
  id: z.string(),
  description: z.string(),
  action: BrowserActionSchema,
  expectedOutcome: z.string(),
  fallback: z.string().optional(),
  confidence: z.number().min(0).max(1),
});
export type WorkflowStep = z.infer<typeof WorkflowStepSchema>;

export const ServiceWorkflowSchema = z.object({
  serviceId: z.string(),
  capability: ServiceCapabilitySchema,
  version: z.string(),
  steps: z.array(WorkflowStepSchema),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  successCount: z.number().default(0),
  failureCount: z.number().default(0),
});
export type ServiceWorkflow = z.infer<typeof ServiceWorkflowSchema>;

export const HealthCheckSchema = z.object({
  status: z.enum(["healthy", "degraded", "unhealthy"]),
  timestamp: z.string().datetime(),
  services: z.record(
    z.object({
      status: z.enum(["healthy", "degraded", "unhealthy"]),
      latency: z.number().optional(),
      error: z.string().optional(),
    })
  ),
});
export type HealthCheck = z.infer<typeof HealthCheckSchema>;

export const APIResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: z
      .object({
        code: z.string(),
        message: z.string(),
        details: z.record(z.unknown()).optional(),
      })
      .optional(),
    meta: z
      .object({
        requestId: z.string(),
        timestamp: z.string().datetime(),
      })
      .optional(),
  });

export type APIResponse<T> = {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  meta?: {
    requestId: string;
    timestamp: string;
  };
};

export const PaginationSchema = z.object({
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(100).default(20),
  total: z.number().int().nonnegative().optional(),
  totalPages: z.number().int().nonnegative().optional(),
});
export type Pagination = z.infer<typeof PaginationSchema>;

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(
  itemSchema: T
) =>
  z.object({
    items: z.array(itemSchema),
    pagination: PaginationSchema,
  });

export type PaginatedResponse<T> = {
  items: T[];
  pagination: Pagination;
};