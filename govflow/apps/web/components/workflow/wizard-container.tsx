"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  WIZARD_STEPS,
  type WizardStep,
  type WorkflowMode,
  type WorkflowData,
} from "./types";
import { ChevronLeft, ChevronRight, Check } from "lucide-react";

interface WizardContainerProps {
  mode: WorkflowMode;
  currentStep: WizardStep;
  onStepChange: (step: WizardStep) => void;
  workflowData: WorkflowData;
  onBack?: () => void;
  onNext?: () => void;
  onSubmit?: () => void;
  isSubmitting?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function WizardContainer({
  mode,
  currentStep,
  onStepChange,
  workflowData,
  onBack,
  onNext,
  onSubmit,
  isSubmitting = false,
  children,
  className,
}: WizardContainerProps) {
  const currentStepIndex = WIZARD_STEPS.findIndex((s) => s.id === currentStep);
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === WIZARD_STEPS.length - 1;

  const getStepStatus = (stepIndex: number) => {
    if (stepIndex < currentStepIndex) return "completed";
    if (stepIndex === currentStepIndex) return "current";
    return "upcoming";
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      <div className="border-b border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950 sm:px-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
              {mode === "apply" ? "Apply for Service" : "Update Records"}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Step {currentStepIndex + 1} of {WIZARD_STEPS.length}:{" "}
              {WIZARD_STEPS[currentStepIndex].description}
            </p>
          </div>
          <Badge variant={mode === "apply" ? "default" : "info"}>
            {mode === "apply" ? "New Application" : "Update Request"}
          </Badge>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          {WIZARD_STEPS.map((step, index) => {
            const status = getStepStatus(index);
            return (
              <React.Fragment key={step.id}>
                <button
                  onClick={() => {
                    if (status === "completed") onStepChange(step.id);
                  }}
                  disabled={status === "upcoming"}
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium transition-colors shrink-0",
                    status === "completed" &&
                      "bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400 cursor-pointer",
                    status === "current" &&
                      "bg-gov-blue text-white",
                    status === "upcoming" &&
                      "bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500 cursor-not-allowed"
                  )}
                  title={step.label}
                >
                  {status === "completed" ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    index + 1
                  )}
                </button>
                {index < WIZARD_STEPS.length - 1 && (
                  <div
                    className={cn(
                      "hidden sm:block h-0.5 flex-1 rounded-full",
                      index < currentStepIndex
                        ? "bg-green-300 dark:bg-green-700"
                        : "bg-slate-200 dark:bg-slate-700"
                    )}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">{children}</div>

      <div className="border-t border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950 sm:px-6">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={onBack}
            disabled={isFirstStep}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back
          </Button>

          <div className="flex items-center gap-2">
            {isLastStep ? (
              <Button onClick={onSubmit} disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <span className="mr-2">Submitting</span>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  </>
                ) : (
                  <>
                    Submit Application
                    <Check className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            ) : (
              <Button onClick={onNext}>
                Continue
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
