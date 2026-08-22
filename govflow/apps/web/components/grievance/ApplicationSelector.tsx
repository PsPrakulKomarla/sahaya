"use client";

import { cn } from "@/lib/utils";
import type { RecentApplication } from "@/lib/api/types";
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileText,
  ChevronRight,
} from "lucide-react";

interface ApplicationSelectorProps {
  applications: RecentApplication[];
  selectedId: string | null;
  onSelect: (app: RecentApplication) => void;
}

const STATUS_ICON: Record<string, React.ElementType> = {
  approved: CheckCircle2,
  under_review: Clock,
  pending_action: AlertTriangle,
  submitted: Clock,
  draft: FileText,
  rejected: AlertTriangle,
  expired: Clock,
};

const STATUS_COLOR: Record<string, string> = {
  approved:
    "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  under_review:
    "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  pending_action:
    "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  submitted:
    "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  draft: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400",
  rejected:
    "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  expired:
    "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-400",
};

const STATUS_LABEL: Record<string, string> = {
  approved: "Approved",
  under_review: "Under Review",
  pending_action: "Action Required",
  submitted: "Submitted",
  draft: "Draft",
  rejected: "Rejected",
  expired: "Expired",
};

export function ApplicationSelector({
  applications,
  selectedId,
  onSelect,
}: ApplicationSelectorProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Your Applications
      </h3>
      <p className="text-xs text-slate-400 dark:text-slate-500">
        Select an application to file a grievance against it.
      </p>
      <div className="space-y-2">
        {applications.map((app) => {
          const isSelected = app.id === selectedId;
          const Icon = STATUS_ICON[app.status] || Clock;
          const statusColor = STATUS_COLOR[app.status] || STATUS_COLOR.draft;
          const statusLabel = STATUS_LABEL[app.status] || app.status;

          return (
            <button
              key={app.id}
              type="button"
              onClick={() => onSelect(app)}
              className={cn(
                "w-full rounded-xl border p-3 text-left transition-all",
                isSelected
                  ? "border-gov-blue bg-blue-50 shadow-sm dark:border-gov-blue-light dark:bg-blue-950/20"
                  : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
                    {app.service}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                    {app.referenceNumber}
                  </p>
                </div>
                <div className="flex items-center gap-1.5">
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium",
                      statusColor
                    )}
                  >
                    <Icon className="h-3 w-3" />
                    {statusLabel}
                  </span>
                  <ChevronRight
                    className={cn(
                      "h-4 w-4 flex-shrink-0 transition-colors",
                      isSelected
                        ? "text-gov-blue"
                        : "text-slate-300 dark:text-slate-600"
                    )}
                  />
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
