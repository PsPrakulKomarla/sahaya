import { useEffect, useState } from "react";
import Link from "next/link";
import { mockRecentApplicationsApi } from "@/lib/mock-data";
import type { RecentApplication } from "@/lib/api/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/lib/utils";

/** Demo citizen whose applications are shown (mock only). */
const DEMO_USER_ID = "demo-citizen-01";

export function RecentApplications() {
  const [applications, setApplications] = useState<RecentApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    mockRecentApplicationsApi
      .getRecentApplications(DEMO_USER_ID)
      .then((data) => {
        if (active) setApplications(data);
      })
      .catch(() => {
        if (active) setError("Could not load applications.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="w-full max-w-4xl mx-auto">
      <div className="mb-4 flex items-baseline justify-between">
        <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400">
          Recent Applications
        </h2>
        <Link
          href="/applications"
          className="text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          View all →
        </Link>
      </div>

      {error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : loading ? (
        <div className="space-y-3">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      ) : applications.length === 0 ? (
        <div className="card py-10 text-center">
          <p className="text-slate-500 dark:text-slate-400">
            You have no recent applications.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((application) => (
            <RecentApplicationCard
              key={application.id}
              application={application}
            />
          ))}
        </div>
      )}
    </section>
  );
}

/**
 * Reusable card that displays the key details of a single application:
 * service, status, date and reference number.
 */
export function RecentApplicationCard({
  application,
}: {
  application: RecentApplication;
}) {
  return (
    <div
      className="card flex items-center justify-between"
      data-testid="application-card"
    >
      <div className="space-y-1">
        <h3 className="font-semibold text-slate-900 dark:text-white">
          {application.service}
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Reference: {application.referenceNumber ?? "—"}
        </p>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          {formatDate(application.date)}
        </p>
        {application.nextAction && (
          <p className="text-xs text-amber-600 dark:text-amber-400">
            Next: {application.nextAction}
          </p>
        )}
      </div>
      <div className="flex items-center gap-3">
        <StatusBadge status={application.status} />
        <Link
          href={`/applications/${application.id}`}
          className="text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          Open
        </Link>
      </div>
    </div>
  );
}