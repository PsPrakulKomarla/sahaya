import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ClipboardList,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

const applications = [
  {
    id: 1,
    service: "Income Certificate",
    department: "Revenue Department",
    appliedDate: "2024-03-15",
    status: "pending",
    estimatedCompletion: "2024-03-20",
    progress: 60,
  },
  {
    id: 2,
    service: "Aadhaar Update",
    department: "UIDAI",
    appliedDate: "2024-03-10",
    status: "approved",
    completedDate: "2024-03-12",
    progress: 100,
  },
  {
    id: 3,
    service: "Driving License",
    department: "Transport Department",
    appliedDate: "2024-03-05",
    status: "in-progress",
    estimatedCompletion: "2024-03-25",
    progress: 40,
  },
  {
    id: 4,
    service: "Property Tax",
    department: "Municipal Corporation",
    appliedDate: "2024-02-28",
    status: "completed",
    completedDate: "2024-02-28",
    progress: 100,
  },
  {
    id: 5,
    service: "Birth Certificate",
    department: "Civil Registration",
    appliedDate: "2024-02-20",
    status: "rejected",
    rejectedDate: "2024-02-25",
    reason: "Missing documents",
    progress: 0,
  },
];

const statusConfig = {
  pending: {
    label: "Pending",
    icon: Clock,
    color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
  },
  approved: {
    label: "Approved",
    icon: CheckCircle,
    color: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  },
  "in-progress": {
    label: "In Progress",
    icon: AlertCircle,
    color: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  },
  completed: {
    label: "Completed",
    icon: CheckCircle,
    color: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  },
  rejected: {
    label: "Rejected",
    icon: XCircle,
    color: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  },
};

export default function ApplicationsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Breadcrumb />

        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            My Applications
          </h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Track the status of your government service applications
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {Object.entries(statusConfig).map(([status, config]) => {
            const count = applications.filter((app) => app.status === status).length;
            return (
              <Card key={status}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-lg ${config.color}`}
                    >
                      <config.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">
                        {count}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {config.label}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {applications.map((app) => {
            const status = statusConfig[app.status as keyof typeof statusConfig];
            return (
              <Card key={app.id}>
                <CardContent className="p-4">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-10 w-10 items-center justify-center rounded-lg ${status.color}`}
                      >
                        <status.icon className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">
                          {app.service}
                        </p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          {app.department}
                        </p>
                      </div>
                    </div>
                    <div className="flex-1 sm:text-right">
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        Applied: {app.appliedDate}
                      </p>
                      {app.estimatedCompletion && (
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          Est. Completion: {app.estimatedCompletion}
                        </p>
                      )}
                      {app.reason && (
                        <p className="text-sm text-red-500">
                          Reason: {app.reason}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={app.status === "rejected" ? "destructive" : "default"}>
                        {status.label}
                      </Badge>
                      <Button variant="ghost" size="icon" asChild>
                        <Link href={`/applications/${app.id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                  {app.progress > 0 && app.progress < 100 && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                        <span>Progress</span>
                        <span>{app.progress}%</span>
                      </div>
                      <div className="mt-1 h-2 rounded-full bg-slate-200 dark:bg-slate-800">
                        <div
                          className="h-2 rounded-full bg-gov-blue"
                          style={{ width: `${app.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </DashboardLayout>
  );
}
