import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { ApprovalPage } from "@/components/approval/ApprovalPage";

export default function ApprovalRoute() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Breadcrumb />
        <ApprovalPage />
      </div>
    </DashboardLayout>
  );
}
