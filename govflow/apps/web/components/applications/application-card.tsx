"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Eye,
  ArrowRight,
  Calendar,
  Hash,
} from "lucide-react";
import type { Application, ApplicationStatus } from "./types";

const statusIcons: Record<ApplicationStatus, React.ElementType> = {
  draft: FileText,
  submitted: Clock,
  processing: AlertCircle,
  approved: CheckCircle,
  rejected: XCircle,
};

const statusBadgeVariant: Record<ApplicationStatus, "default" | "secondary" | "destructive" | "success" | "warning" | "info" | "outline"> = {
  draft: "outline",
  submitted: "info",
  processing: "warning",
  approved: "success",
  rejected: "destructive",
};

interface ApplicationCardProps {
  application: Application;
  className?: string;
}

export function ApplicationCard({ application, className }: ApplicationCardProps) {
  const StatusIcon = statusIcons[application.status];

  return (
    <Card className={cn("hover:shadow-md transition-shadow", className)}>
      <CardContent className="p-4 sm:p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
          <div className="flex items-start gap-3">
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-lg shrink-0",
                application.status === "approved"
                  ? "bg-green-100 dark:bg-green-900/30"
                  : application.status === "rejected"
                  ? "bg-red-100 dark:bg-red-900/30"
                  : application.status === "processing"
                  ? "bg-yellow-100 dark:bg-yellow-900/30"
                  : application.status === "submitted"
                  ? "bg-blue-100 dark:bg-blue-900/30"
                  : "bg-slate-100 dark:bg-slate-800"
              )}
            >
              <StatusIcon
                className={cn(
                  "h-5 w-5",
                  application.status === "approved"
                    ? "text-green-600 dark:text-green-400"
                    : application.status === "rejected"
                    ? "text-red-600 dark:text-red-400"
                    : application.status === "processing"
                    ? "text-yellow-600 dark:text-yellow-400"
                    : application.status === "submitted"
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-slate-500 dark:text-slate-400"
                )}
              />
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-slate-900 dark:text-white truncate">
                {application.serviceName}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400 truncate">
                {application.department}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 sm:ml-auto">
            <Badge variant={statusBadgeVariant[application.status]}>
              {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
            </Badge>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
            <Hash className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate font-mono text-xs">{application.referenceNumber}</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
            <Calendar className="h-3.5 w-3.5 shrink-0" />
            <span className="text-xs">{new Date(application.appliedDate).toLocaleDateString("en-IN")}</span>
          </div>
          {application.estimatedCompletion && (
            <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
              <Clock className="h-3.5 w-3.5 shrink-0" />
              <span className="text-xs">Est. {application.estimatedCompletion}</span>
            </div>
          )}
          {application.completedDate && (
            <div className="flex items-center gap-1.5 text-green-600 dark:text-green-400">
              <CheckCircle className="h-3.5 w-3.5 shrink-0" />
              <span className="text-xs">Completed {application.completedDate}</span>
            </div>
          )}
        </div>

        {application.rejectionReason && (
          <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-900 dark:bg-red-900/20">
            <p className="text-xs text-red-700 dark:text-red-300">
              <strong>Rejection Reason:</strong> {application.rejectionReason}
            </p>
          </div>
        )}

        {application.progress > 0 && application.progress < 100 && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>Progress</span>
              <span>{application.progress}%</span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-slate-200 dark:bg-slate-800">
              <div
                className="h-1.5 rounded-full bg-gov-blue transition-all"
                style={{ width: `${application.progress}%` }}
              />
            </div>
          </div>
        )}

        <div className="mt-4 flex items-center gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
          <Button variant="outline" size="sm" asChild>
            <Link href={`/applications/${application.id}`}>
              <Eye className="mr-1.5 h-3.5 w-3.5" />
              View Details
            </Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/applications/${application.id}`}>
              Check Status
              <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
