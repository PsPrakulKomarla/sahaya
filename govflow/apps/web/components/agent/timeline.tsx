"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import {
  Brain,
  Globe,
  BookOpen,
  CheckCircle,
  FileSearch,
  Route,
  ClipboardCheck,
  Loader2,
  Circle,
} from "lucide-react";

export type TimelineStep =
  | "understanding"
  | "finding_portal"
  | "reading_requirements"
  | "checking_eligibility"
  | "waiting_documents"
  | "planning_workflow"
  | "ready";

interface StepConfig {
  id: TimelineStep;
  label: string;
  description: string;
  icon: React.ElementType;
}

const defaultSteps: StepConfig[] = [
  {
    id: "understanding",
    label: "Understanding request",
    description: "Analyzing your requirements",
    icon: Brain,
  },
  {
    id: "finding_portal",
    label: "Finding official portal",
    description: "Locating the right government website",
    icon: Globe,
  },
  {
    id: "reading_requirements",
    label: "Reading requirements",
    description: "Checking documents and eligibility",
    icon: BookOpen,
  },
  {
    id: "checking_eligibility",
    label: "Checking eligibility",
    description: "Verifying you qualify for this service",
    icon: CheckCircle,
  },
  {
    id: "waiting_documents",
    label: "Waiting for documents",
    description: "Awaiting your document uploads",
    icon: FileSearch,
  },
  {
    id: "planning_workflow",
    label: "Planning workflow",
    description: "Mapping out the application steps",
    icon: Route,
  },
  {
    id: "ready",
    label: "Ready",
    description: "All set to proceed",
    icon: ClipboardCheck,
  },
];

interface TimelineProps {
  currentStep: TimelineStep;
  steps?: StepConfig[];
  className?: string;
}

export function Timeline({
  currentStep,
  steps = defaultSteps,
  className,
}: TimelineProps) {
  const currentIndex = steps.findIndex((s) => s.id === currentStep);

  const getStepStatus = (index: number): "completed" | "current" | "upcoming" => {
    if (index < currentIndex) return "completed";
    if (index === currentIndex) return "current";
    return "upcoming";
  };

  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950", className)}>
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-3">
        Agent Progress
      </p>
      <div className="space-y-0">
        {steps.map((step, index) => {
          const status = getStepStatus(index);
          const StepIcon = step.icon;

          return (
            <div key={step.id} className="flex gap-3">
              {/* Line + Icon */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-full border-2 transition-colors",
                    status === "completed" &&
                      "border-green-500 bg-green-50 dark:bg-green-900/20",
                    status === "current" &&
                      "border-gov-blue bg-gov-blue/10 animate-pulse",
                    status === "upcoming" &&
                      "border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900"
                  )}
                >
                  {status === "completed" ? (
                    <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                  ) : status === "current" ? (
                    <Loader2 className="h-4 w-4 text-gov-blue animate-spin" />
                  ) : (
                    <Circle className="h-4 w-4 text-slate-300 dark:text-slate-600" />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      "w-0.5 h-6",
                      status === "completed"
                        ? "bg-green-500"
                        : "bg-slate-200 dark:bg-slate-700"
                    )}
                  />
                )}
              </div>

              {/* Content */}
              <div className="pb-4 pt-1">
                <p
                  className={cn(
                    "text-sm font-medium",
                    status === "completed" &&
                      "text-green-600 dark:text-green-400",
                    status === "current" && "text-gov-blue",
                    status === "upcoming" &&
                      "text-slate-400 dark:text-slate-500"
                  )}
                >
                  {step.label}
                </p>
                {status === "current" && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {step.description}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
