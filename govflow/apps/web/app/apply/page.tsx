import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { ServiceWorkflow, applyWorkflowConfig } from "@/components/workflow";

export default function ApplyPage() {
  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-4rem)]">
        <Breadcrumb />
        <ServiceWorkflow
          mode="apply"
          services={applyWorkflowConfig.services}
          eligibility={applyWorkflowConfig.eligibility}
          documents={applyWorkflowConfig.documents}
          formSections={applyWorkflowConfig.formSections}
        />
      </div>
    </DashboardLayout>
  );
}
