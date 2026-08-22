import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import { ApplicationCard } from "@/components/applications/application-card";
import { ApplicationFilters } from "@/components/applications/application-filters";
import { ApplicationTimeline } from "@/components/applications/application-timeline";
import type { Application } from "@/components/applications/types";
import { mockApplications } from "@/components/applications/mock-data";
import Link from "next/link";
import * as React from "react";

export default function ApplicationsPage() {
  const [filters, setFilters] = React.useState<{
    status: "all" | "draft" | "submitted" | "processing" | "approved" | "rejected";
    search: string;
  }>({ status: "all", search: "" });

  const filteredApplications = mockApplications.filter((app) => {
    const matchesStatus =
      filters.status === "all" || app.status === filters.status;
    const matchesSearch =
      !filters.search ||
      app.serviceName
        .toLowerCase()
        .includes(filters.search.toLowerCase()) ||
      app.referenceNumber.toLowerCase().includes(filters.search.toLowerCase()) ||
      app.department.toLowerCase().includes(filters.search.toLowerCase());

    return matchesStatus && matchesSearch;
  });

  const counts = {
    all: mockApplications.length,
    draft: mockApplications.filter((a) => a.status === "draft").length,
    submitted: mockApplications.filter((a) => a.status === "submitted").length,
    processing: mockApplications.filter((a) => a.status === "processing").length,
    approved: mockApplications.filter((a) => a.status === "approved").length,
    rejected: mockApplications.filter((a) => a.status === "rejected").length,
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-4rem)]">
        <Breadcrumb />

        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Filters */}
          <div className="border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-950">
            <ApplicationFilters
              activeFilter={filters.status}
              searchQuery={filters.search}
              onFilterChange={(status) =>
                setFilters((prev) => ({ ...prev, status }))
              }
              onSearchChange={(query) => setFilters((prev) => ({ ...prev, search: query }))}
              counts={counts}
            />
          </div>

          {/* Applications Grid */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 overflow-x-hidden">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filteredApplications.map((app) => {
                return <ApplicationCard key={app.id} application={app} />;
              })}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}