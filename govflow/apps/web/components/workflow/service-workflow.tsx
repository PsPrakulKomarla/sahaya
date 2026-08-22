"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { WizardContainer } from "./wizard-container";
import { ServiceStep, EligibilityStep, DocumentsStep, InformationStep, ReviewSummary, ApprovalStep } from "./steps";
import type {
  WizardStep,
  WorkflowMode,
  WorkflowData,
  ServiceOption,
  EligibilityCriteria,
  DocumentRequirement,
  FormSection,
} from "./types";

interface ServiceWorkflowProps {
  mode: WorkflowMode;
  services: ServiceOption[];
  eligibility: EligibilityCriteria[];
  documents: DocumentRequirement[];
  formSections: FormSection[];
  className?: string;
  onComplete?: (data: WorkflowData) => void;
}

const STEP_ORDER: WizardStep[] = [
  "service",
  "eligibility",
  "documents",
  "information",
  "review",
  "approval",
];

export function ServiceWorkflow({
  mode,
  services,
  eligibility,
  documents,
  formSections,
  className,
  onComplete,
}: ServiceWorkflowProps) {
  const [currentStep, setCurrentStep] = React.useState<WizardStep>("service");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [workflowData, setWorkflowData] = React.useState<WorkflowData>({
    mode,
    eligibility,
    documents,
    formData: {},
  });

  const currentStepIndex = STEP_ORDER.indexOf(currentStep);

  const handleStepChange = (step: WizardStep) => {
    setCurrentStep(step);
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(STEP_ORDER[currentStepIndex - 1]);
    }
  };

  const handleNext = () => {
    if (currentStepIndex < STEP_ORDER.length - 1) {
      setCurrentStep(STEP_ORDER[currentStepIndex + 1]);
    }
  };

  const handleServiceSelect = (service: ServiceOption) => {
    setWorkflowData((prev) => ({ ...prev, service }));
  };

  const handleFieldChange = (fieldId: string, value: string) => {
    setWorkflowData((prev) => ({
      ...prev,
      formData: { ...prev.formData, [fieldId]: value },
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsSubmitting(false);
    setCurrentStep("approval");
    onComplete?.(workflowData);
  };

  const handleDocumentUpload = (documentId: string) => {
    setWorkflowData((prev) => ({
      ...prev,
      documents: prev.documents?.map((doc) =>
        doc.id === documentId ? { ...doc, status: "uploaded" as const, uploadedAt: new Date().toISOString().split("T")[0] } : doc
      ),
    }));
  };

  const handleDocumentRemove = (documentId: string) => {
    setWorkflowData((prev) => ({
      ...prev,
      documents: prev.documents?.map((doc) =>
        doc.id === documentId ? { ...doc, status: "required" as const, uploadedAt: undefined } : doc
      ),
    }));
  };

  const canProceed = () => {
    switch (currentStep) {
      case "service":
        return !!workflowData.service;
      case "eligibility":
        return true;
      case "documents":
        return true;
      case "information":
        return true;
      case "review":
        return true;
      case "approval":
        return true;
      default:
        return false;
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case "service":
        return (
          <ServiceStep
            services={services}
            selectedService={workflowData.service}
            onSelect={handleServiceSelect}
          />
        );
      case "eligibility":
        return <EligibilityStep criteria={workflowData.eligibility ?? eligibility} />;
      case "documents":
        return (
          <DocumentsStep
            documents={workflowData.documents ?? documents}
            onUpload={handleDocumentUpload}
            onRemove={handleDocumentRemove}
          />
        );
      case "information":
        return (
          <InformationStep
            sections={formSections}
            formData={workflowData.formData ?? {}}
            onFieldChange={handleFieldChange}
          />
        );
      case "review":
        return <ReviewSummary workflowData={workflowData} />;
      case "approval":
        return (
          <ApprovalStep
            referenceNumber="GOV/2024/001234"
            serviceName={workflowData.service?.name}
            estimatedTime={workflowData.service?.estimatedTime}
          />
        );
      default:
        return null;
    }
  };

  return (
    <WizardContainer
      mode={mode}
      currentStep={currentStep}
      onStepChange={handleStepChange}
      workflowData={workflowData}
      onBack={handleBack}
      onNext={canProceed() ? handleNext : undefined}
      onSubmit={handleSubmit}
      isSubmitting={isSubmitting}
      className={className}
    >
      {renderStep()}
    </WizardContainer>
  );
}
