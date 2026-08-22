export type ApplicationStatus =
  | "draft"
  | "submitted"
  | "processing"
  | "approved"
  | "rejected";

export type TimelineStatus =
  | "draft"
  | "submitted"
  | "under_review"
  | "processing"
  | "completed"
  | "rejected";

export interface ApplicationDocument {
  id: string;
  name: string;
  status: "uploaded" | "verified" | "rejected";
  uploadedAt?: string;
}

export interface TimelineEvent {
  id: string;
  status: TimelineStatus;
  label: string;
  description?: string;
  timestamp: string;
  completed: boolean;
}

export interface Application {
  id: string;
  serviceId: string;
  serviceName: string;
  department: string;
  status: ApplicationStatus;
  referenceNumber: string;
  appliedDate: string;
  lastUpdated: string;
  estimatedCompletion?: string;
  completedDate?: string;
  rejectionReason?: string;
  progress: number;
  timeline: TimelineEvent[];
  documents: ApplicationDocument[];
  applicantName: string;
  contactPhone: string;
  contactEmail?: string;
}

export interface ApplicationFilters {
  status: ApplicationStatus | "all";
  search: string;
}

export const STATUS_CONFIG: Record<
  ApplicationStatus,
  { label: string; color: string; bgColor: string }
> = {
  draft: {
    label: "Draft",
    color: "text-slate-600 dark:text-slate-400",
    bgColor: "bg-slate-100 dark:bg-slate-800",
  },
  submitted: {
    label: "Submitted",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
  },
  processing: {
    label: "Processing",
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
  },
  approved: {
    label: "Approved",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
  },
  rejected: {
    label: "Rejected",
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-100 dark:bg-red-900/30",
  },
};

export const TIMELINE_STATUS_CONFIG: Record<
  TimelineStatus,
  { label: string; color: string }
> = {
  draft: { label: "Draft", color: "text-slate-500" },
  submitted: { label: "Submitted", color: "text-blue-600" },
  under_review: { label: "Under Review", color: "text-yellow-600" },
  processing: { label: "Processing", color: "text-orange-600" },
  completed: { label: "Completed", color: "text-green-600" },
  rejected: { label: "Rejected", color: "text-red-600" },
};
