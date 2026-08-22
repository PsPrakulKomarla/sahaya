import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { Button } from "@/components/ui/button";
import { DocumentCenter } from "@/components/documents/DocumentCenter";
import { Upload } from "lucide-react";

export default function DocumentsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Breadcrumb />

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Document Center
            </h1>
            <p className="mt-1 text-slate-600 dark:text-slate-400">
              Upload, manage, and verify your government documents securely
            </p>
          </div>
        </div>

        <DocumentCenter />
      </div>
    </DashboardLayout>
  );
}
