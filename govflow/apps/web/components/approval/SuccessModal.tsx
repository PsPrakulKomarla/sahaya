"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";
import type { ApprovalResult } from "@/lib/api/types";
import {
  CheckCircle2,
  Copy,
  FileText,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

interface SuccessModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  result: ApprovalResult | null;
}

export function SuccessModal({ open, onOpenChange, result }: SuccessModalProps) {
  if (!result) return null;

  const handleCopyRef = () => {
    navigator.clipboard.writeText(result.referenceNumber);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        {/* Success illustration */}
        <div className="flex flex-col items-center text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
            <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <DialogTitle className="mt-4 text-xl">
            Application Submitted
          </DialogTitle>
          <DialogDescription className="mt-1">
            Your application has been successfully submitted for processing.
          </DialogDescription>
        </div>

        {/* Reference number card */}
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
            Reference Number
          </p>
          <div className="mt-1 flex items-center justify-between">
            <p className="font-mono text-lg font-bold text-slate-900 dark:text-white">
              {result.referenceNumber}
            </p>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopyRef}
              className="gap-1 text-xs"
              aria-label="Copy reference number"
            >
              <Copy className="h-3 w-3" />
              Copy
            </Button>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Submitted {formatDate(result.submittedAt)}
          </p>
        </div>

        {/* Next steps */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
            What happens next
          </h4>
          <ol className="space-y-2">
            {result.nextSteps.map((step, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-gov-blue/10 text-[10px] font-bold text-gov-blue">
                  {i + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 pt-2">
          <Button className="w-full gap-2" onClick={() => onOpenChange(false)}>
            <FileText className="h-4 w-4" />
            View Application Status
            <ArrowRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="w-full gap-2"
            onClick={() => onOpenChange(false)}
          >
            <ExternalLink className="h-4 w-4" />
            Track on Portal
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
