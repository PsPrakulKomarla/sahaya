import type { ApplicationStatus } from "@govflow/shared";
import { cn } from "@/lib/utils";
import { APPLICATION_STATUS_LABELS } from "@/lib/mock-data";

const STATUS_COLORS: Record<ApplicationStatus, string> = {
  draft: "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
  submitted:
    "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  under_review:
    "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  approved:
    "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  pending_action:
    "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300",
  expired:
    "bg-slate-300 text-slate-600 dark:bg-slate-600 dark:text-slate-400",
};

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        STATUS_COLORS[status]
      )}
    >
      {APPLICATION_STATUS_LABELS[status]}
    </span>
  );
}