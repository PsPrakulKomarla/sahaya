import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { ApplicationCard } from "@/components/applications/application-card";
import { ApplicationTimeline } from "@/components/applications/application-timeline";
import type { Application } from "@/components/applications/types";
import { ApplicationStatus } from "@/components/applications/types";
import { mockApplications } from "@/components/applications/mock-data";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface ApplicationDetailsProps {
  params: { id: string };
}

export function ApplicationDetails({ params }: ApplicationDetailsProps) {
  const application = mockApplications.find((app) => app.id === params.id);

  if (!application) {
    return (
      <DashboardLayout>
        <div className="p-8 text-center">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Application Not Found
          </h1>
          <p className="mt-4 text-slate-600 dark:text-slate-400">
            The application you requested does not exist.
          </p>
          <Button onClick={() => window.history.back()}>Back to Applications</Button>
        </div>
      </DashboardLayout>
    );
  }

  const status = application.status as ApplicationStatus;

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-4rem)]">
        <Breadcrumb />

        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Application Header */}
          <div className="border-b border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  {application.serviceName}
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {application.department}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <Badge variant={status === "rejected" ? "destructive" : status === "approved" ? "success" : status === "processing" ? "warning" : "info"}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </Badge>
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {application.referenceNumber}
                </span>
              </div>
            </div>
          </div>

          {/* Application Card */}
          <div className="p-4 sm:p-5">
            <ApplicationCard application={application} />
          </div>

          {/* Timeline */}
          <ApplicationTimeline events={application.timeline} />

          {/* Documents */}
          {!application.documents.length ? (
            <div className="p-4 sm:p-5 text-center">
              <p className="text-slate-500 dark:text-slate-400">
                No documents uploaded yet
              </p>
            </div>
          ) : (
            <div className="p-4 sm:p-5">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Documents
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {application.documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={cn(
                      "flex items-center gap-2 rounded bg-slate-50 dark:bg-slate-900 p-3",
                      doc.status === "verified"
                        ? "bg-green-50 dark:bg-green-900/30"
                        : doc.status === "uploaded"
                        ? "bg-blue-50 dark:bg-blue-900/30"
                        : "bg-red-50 dark:bg-red-900/30"
                    )}
                  >
                    <div
                      className={cn(
                        "flex h-8 w-8 items-center justify-center rounded-lg shrink-0",
                        doc.status === "verified"
                          ? "bg-green-100 dark:bg-green-900/30"
                          : doc.status === "uploaded"
                          ? "bg-blue-100 dark:bg-blue-900/30"
                          : "bg-red-100 dark:bg-red-900/30"
                      )}
                    >
                      {doc.status === "verified" ? (
                        <svg
                          className="h-4 w-4 text-green-600 dark:text-green-400"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                        >
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      ) : doc.status === "uploaded" ? (
                        <svg
                          className="h-4 w-4 text-blue-600 dark:text-blue-400"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                        >
                          <path
                            d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M5 3v4H3a1 1 0 00-1 1v14a1 1 0 001 1h6a1 1 0 001-1v-1h4v1h6v-1h4v-1h6v-1h4v-1H5a1 1 0 00-1 1v4zm0-2v2h14v2l4-4h-4l-4 4H5l4-4z"
                          />
                        </svg>
                      ) : doc.status === "uploaded" ? (
                        <svg
                          className="h-4 w-4 text-blue-600 dark:text-blue-400"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                        >
                          <path
                            d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M5 3v4H3a1 1 0 00-1 1v14a1 1 0 001 1h6a1 1 0 001-1v-1h4v1h6v-1h4v-1h6v-1h4v-1H5a1 1 0 00-1 1v4zm0-2v2h14v2l4-4h-4l-4 4H5l4-4z"
                          />
                        </svg>
                      ) : (
                        <svg
                          className="h-4 w-4 text-red-600 dark:text-red-400"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                        >
                          <path
                            d="M31.6 11.4l-.7-1.7a2.4 2.4 0 00-1.7-.7L12 4.5l-3.2 2.1.8 2.1a2.4 2.4 0 001.7.6l.7 1.7c.6.8 1.2 1.6 1.9 2.4.8.8 1.5 1.5 1.9 2.5.5.9-.8 1.5-1.4 1.4L12 15.5l3.1-1.5a2.4 2.4 0 00.7-1.6l-.6-1.6a2.4 2.4 0 00-1.8-.6zM5 11.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"
                          />
                        </svg>
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                        {doc.name}
                      </p>
                      <Badge
                        variant={doc.status === "verified" ? "outline" : doc.status === "uploaded" ? "info" : "destructive"}
                        className="text-[10px] ml-auto"
                      >
                        {doc.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Back button */}
        <div className="border-t border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => window.history.back()}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-slate-500 dark:text-slate-400">
              Go back to applications
            </span>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}