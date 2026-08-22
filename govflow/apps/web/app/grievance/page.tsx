import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { GrievanceCenter } from "@/components/grievance/GrievanceCenter";

export default function GrievancePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Breadcrumb />
        <GrievanceCenter />
      </div>
    </DashboardLayout>
  );
}