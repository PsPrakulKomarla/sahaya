"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";
import type {
  RecentApplication,
  GrievanceCategory,
  GrievanceSubmitResult,
} from "@/lib/api/types";
import { GRIEVANCE_CATEGORY_LABELS } from "@/lib/api/types";
import {
  AlertTriangle,
  CheckCircle2,
  Send,
  X,
  Copy,
  FileText,
} from "lucide-react";

interface GrievanceApprovalModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  application: RecentApplication | null;
  category: GrievanceCategory | "";
  description: string;
  attachmentCount: number;
  onConfirm: () => void;
  isSubmitting: boolean;
  result: GrievanceSubmitResult | null;
}

export function GrievanceApprovalModal({
  open,
  onOpenChange,
  application,
  category,
  description,
  attachmentCount,
  onConfirm,
  isSubmitting,
  result,
}: GrievanceApprovalModalProps) {
  const handleCopyTicket = () => {
    if (result) navigator.clipboard.writeText(result.ticketId);
  };

  // ── Success state ──
  if (result) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <div className="flex flex-col items-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
              <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            <DialogTitle className="mt-4 text-xl">
              Grievance Submitted
            </DialogTitle>
            <DialogDescription className="mt-1">
              Your grievance has been filed successfully. We&apos;ll keep you
              updated.
            </DialogDescription>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Ticket ID
            </p>
            <div className="mt-1 flex items-center justify-between">
              <p className="font-mono text-lg font-bold text-slate-900 dark:text-white">
                {result.ticketId}
              </p>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyTicket}
                className="gap-1 text-xs"
              >
                <Copy className="h-3 w-3" />
                Copy
              </Button>
            </div>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {result.message}
            </p>
          </div>

          <DialogFooter>
            <Button
              className="w-full gap-2"
              onClick={() => onOpenChange(false)}
            >
              <FileText className="h-4 w-4" />
              View My Grievances
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  // ── Confirmation state ──
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Confirm Submission
          </DialogTitle>
          <DialogDescription>
            Please review your grievance details before submitting.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
          {application && (
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Application
              </p>
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {application.service}
              </p>
              <p className="font-mono text-xs text-slate-500 dark:text-slate-400">
                Ref: {application.referenceNumber}
              </p>
            </div>
          )}
          {category && (
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Category
              </p>
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {GRIEVANCE_CATEGORY_LABELS[category as GrievanceCategory]}
              </p>
            </div>
          )}
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Description
            </p>
            <p className="mt-0.5 line-clamp-3 text-sm text-slate-700 dark:text-slate-300">
              {description}
            </p>
          </div>
          {attachmentCount > 0 && (
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Attachments
              </p>
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {attachmentCount} file{attachmentCount !== 1 && "s"} attached
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="gap-1"
          >
            <X className="h-4 w-4" />
            Cancel
          </Button>
          <Button
            onClick={onConfirm}
            disabled={isSubmitting}
            className="gap-1"
          >
            {isSubmitting ? (
              "Submitting..."
            ) : (
              <>
                <Send className="h-4 w-4" />
                Confirm & Submit
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
