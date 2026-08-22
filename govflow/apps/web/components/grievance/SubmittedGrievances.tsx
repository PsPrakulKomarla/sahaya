"use client";

import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type {
  GrievanceTicket,
  GrievanceTicketStatus,
} from "@/lib/api/types";
import { GRIEVANCE_STATUS_LABELS } from "@/lib/api/types";
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  Eye,
  FileText,
  Shield,
} from "lucide-react";

interface SubmittedGrievancesProps {
  tickets: GrievanceTicket[];
}

const STATUS_CONFIG: Record<
  GrievanceTicketStatus,
  { variant: "success" | "info" | "warning" | "destructive" | "secondary"; icon: React.ElementType }
> = {
  submitted: { variant: "info", icon: Clock },
  under_review: { variant: "warning", icon: AlertTriangle },
  in_progress: { variant: "info", icon: Clock },
  resolved: { variant: "success", icon: CheckCircle2 },
  closed: { variant: "secondary", icon: Shield },
};

export function SubmittedGrievances({ tickets }: SubmittedGrievancesProps) {
  if (tickets.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center dark:border-slate-700">
        <FileText className="mx-auto h-8 w-8 text-slate-300 dark:text-slate-600" />
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          No grievances submitted yet.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tickets.map((ticket) => {
        const config = STATUS_CONFIG[ticket.status];
        const StatusIcon = config.icon;

        return (
          <div
            key={ticket.id}
            className="rounded-xl border border-slate-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-mono text-xs font-bold text-slate-900 dark:text-white">
                    {ticket.id}
                  </p>
                  <Badge variant={config.variant} className="gap-1 text-xs">
                    <StatusIcon className="h-3 w-3" />
                    {GRIEVANCE_STATUS_LABELS[ticket.status]}
                  </Badge>
                </div>
                <p className="mt-1 text-sm font-medium text-slate-700 dark:text-slate-300">
                  {ticket.applicationService}
                </p>
                <p className="mt-0.5 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
                  {ticket.description}
                </p>
                <div className="mt-2 flex items-center gap-3 text-xs text-slate-400 dark:text-slate-500">
                  <span>{ticket.department}</span>
                  <span>&middot;</span>
                  <span>Ref: {ticket.referenceNumber}</span>
                  <span>&middot;</span>
                  <span>{formatDate(ticket.createdAt)}</span>
                </div>
              </div>
              {ticket.attachments.length > 0 && (
                <div className="flex-shrink-0 text-xs text-slate-400">
                  {ticket.attachments.length} file
                  {ticket.attachments.length !== 1 && "s"}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
