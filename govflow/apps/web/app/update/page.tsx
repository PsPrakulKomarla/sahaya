import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { ServiceWorkflow, updateWorkflowConfig } from "@/components/workflow";

export default function UpdatePage() {
  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-4rem)]">
        <Breadcrumb />
        <ServiceWorkflow
          mode="update"
          services={updateWorkflowConfig.services}
          eligibility={updateWorkflowConfig.eligibility}
          documents={updateWorkflowConfig.documents}
          formSections={updateWorkflowConfig.formSections}
        />
      </div>
    </DashboardLayout>
  );
}
