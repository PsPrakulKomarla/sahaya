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
  AlertCircle,
  Plus,
  Clock,
  CheckCircle,
  MessageSquare,
  Eye,
} from "lucide-react";
import Link from "next/link";

const grievances = [
  {
    id: 1,
    title: "Delay in Income Certificate processing",
    category: "Processing Delay",
    submittedDate: "2024-03-14",
    status: "open",
    priority: "high",
    responses: 2,
  },
  {
    id: 2,
    title: "Incorrect name on Aadhaar card",
    category: "Data Correction",
    submittedDate: "2024-03-10",
    status: "in-progress",
    priority: "medium",
    responses: 1,
  },
  {
    id: 3,
    title: "Property tax payment not reflected",
    category: "Payment Issue",
    submittedDate: "2024-03-05",
    status: "resolved",
    priority: "low",
    responses: 4,
  },
];

const statusConfig = {
  open: {
    label: "Open",
    color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
  },
  "in-progress": {
    label: "In Progress",
    color: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  },
  resolved: {
    label: "Resolved",
    color: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  },
};

const priorityConfig = {
  high: { label: "High", color: "text-red-600" },
  medium: { label: "Medium", color: "text-yellow-600" },
  low: { label: "Low", color: "text-green-600" },
};

export default function GrievancePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Breadcrumb />

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Grievance Center
            </h1>
            <p className="mt-1 text-slate-600 dark:text-slate-400">
              Report issues and track grievance resolution
            </p>
          </div>
          <Button asChild>
            <Link href="/grievance/new">
              <Plus className="mr-2 h-4 w-4" />
              New Grievance
            </Link>
          </Button>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-100 dark:bg-yellow-900/30">
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {grievances.filter((g) => g.status === "open").length}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Open Grievances
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                  <Clock className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {grievances.filter((g) => g.status === "in-progress").length}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    In Progress
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {grievances.filter((g) => g.status === "resolved").length}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Resolved
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Grievances List */}
        <div className="space-y-4">
          {grievances.map((grievance) => {
            const status = statusConfig[grievance.status as keyof typeof statusConfig];
            const priority = priorityConfig[grievance.priority as keyof typeof priorityConfig];
            return (
              <Card key={grievance.id}>
                <CardContent className="p-4">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-slate-900 dark:text-white">
                          {grievance.title}
                        </p>
                        <Badge variant={grievance.status === "resolved" ? "success" : "default"}>
                          {status.label}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {grievance.category} • Submitted {grievance.submittedDate}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className={`text-sm font-medium ${priority.color}`}>
                          {priority.label} Priority
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {grievance.responses} responses
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" asChild>
                          <Link href={`/grievance/${grievance.id}`}>
                            <MessageSquare className="mr-1 h-4 w-4" />
                            View
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </DashboardLayout>
  );
}
