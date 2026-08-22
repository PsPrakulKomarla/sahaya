"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
} from "lucide-react";
import type { EligibilityCriteria } from "../types";

interface EligibilityCardProps {
  criteria: EligibilityCriteria;
  className?: string;
}

export function EligibilityCard({ criteria, className }: EligibilityCardProps) {
  return (
    <Card
      className={cn(
        "transition-all",
        criteria.met
          ? "border-green-200 dark:border-green-900"
          : criteria.required
          ? "border-red-200 dark:border-red-900"
          : "border-slate-200 dark:border-slate-800",
        className
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-full shrink-0",
              criteria.met
                ? "bg-green-100 dark:bg-green-900/30"
                : criteria.required
                ? "bg-red-100 dark:bg-red-900/30"
                : "bg-slate-100 dark:bg-slate-800"
            )}
          >
            {criteria.met ? (
              <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
            ) : criteria.required ? (
              <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {criteria.label}
              </p>
              {criteria.required && (
                <Badge variant="destructive" className="text-[10px]">
                  Required
                </Badge>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {criteria.description}
            </p>
          </div>
          <Badge
            variant={criteria.met ? "success" : criteria.required ? "destructive" : "warning"}
          >
            {criteria.met ? "Met" : criteria.required ? "Not Met" : "Optional"}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

interface EligibilityStepProps {
  criteria: EligibilityCriteria[];
  className?: string;
}

export function EligibilityStep({ criteria, className }: EligibilityStepProps) {
  const metCount = criteria.filter((c) => c.met).length;
  const requiredCount = criteria.filter((c) => c.required).length;
  const requiredMet = criteria
    .filter((c) => c.required)
    .every((c) => c.met);

  return (
    <div className={cn("p-4 sm:p-6 space-y-4", className)}>
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          Eligibility Check
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Verify that you meet the requirements for this service
        </p>
      </div>

      <div className="flex items-center gap-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
        <Info className="h-5 w-5 text-slate-400" />
        <div className="text-sm">
          <span className="text-slate-600 dark:text-slate-300">
            {metCount} of {criteria.length} criteria met
          </span>
          {!requiredMet && (
            <span className="ml-2 text-red-600 dark:text-red-400">
              ({requiredCount - criteria.filter((c) => c.required && c.met).length} required criteria not met)
            </span>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {criteria.map((item) => (
          <EligibilityCard key={item.id} criteria={item} />
        ))}
      </div>

      {!requiredMet && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-900 dark:bg-yellow-900/20">
          <p className="text-sm text-yellow-800 dark:text-yellow-300">
            <strong>Note:</strong> You must meet all required criteria to proceed.
            Please ensure you have the necessary documents and meet the eligibility requirements.
          </p>
        </div>
      )}
    </div>
  );
}
