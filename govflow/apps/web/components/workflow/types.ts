export type WorkflowMode = "apply" | "update";

export type WizardStep =
  | "service"
  | "eligibility"
  | "documents"
  | "information"
  | "review"
  | "approval";

export interface ServiceOption {
  id: string;
  name: string;
  department: string;
  description: string;
  estimatedTime: string;
  category: string;
}

export interface EligibilityCriteria {
  id: string;
  label: string;
  description: string;
  met: boolean;
  required: boolean;
}

export interface DocumentRequirement {
  id: string;
  name: string;
  description: string;
  status: "required" | "uploaded" | "missing" | "verified";
  file?: File;
  uploadedAt?: string;
  verificationNote?: string;
}

export interface FormField {
  id: string;
  label: string;
  type: "text" | "email" | "phone" | "date" | "select" | "textarea" | "file";
  placeholder?: string;
  required: boolean;
  value?: string;
  options?: Array<{ label: string; value: string }>;
  validation?: {
    pattern?: string;
    minLength?: number;
    maxLength?: number;
    message?: string;
  };
}

export interface FormSection {
  id: string;
  title: string;
  description?: string;
  fields: FormField[];
}

export interface ReviewField {
  label: string;
  value: string;
  editable?: boolean;
  section?: string;
}

export interface WorkflowData {
  mode: WorkflowMode;
  service?: ServiceOption;
  eligibility?: EligibilityCriteria[];
  documents?: DocumentRequirement[];
  formData?: Record<string, string>;
  applicantName?: string;
  submittedAt?: string;
  referenceNumber?: string;
}

export interface WizardConfig {
  mode: WorkflowMode;
  services: ServiceOption[];
  eligibility: EligibilityCriteria[];
  documents: DocumentRequirement[];
  formSections: FormSection[];
}

export const WIZARD_STEPS: { id: WizardStep; label: string; description: string }[] = [
  { id: "service", label: "Service", description: "Select a service" },
  { id: "eligibility", label: "Eligibility", description: "Check requirements" },
  { id: "documents", label: "Documents", description: "Upload documents" },
  { id: "information", label: "Information", description: "Your details" },
  { id: "review", label: "Review", description: "Verify & submit" },
  { id: "approval", label: "Approval", description: "Confirmation" },
];
