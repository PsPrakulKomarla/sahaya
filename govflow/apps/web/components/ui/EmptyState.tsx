import { cn } from "@/lib/utils";
import { Sunrise, AlertCircle, CheckCircle, FolderDownload } from "lucide-react";

export function EmptyState({
  title,
  description,
  actionLabel,
  actionHref,
  icon,
  ...props
}: {
  title: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  icon?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "col-span-1 text-center py-16 px-4",
        "sm:col-span-2 sm:py-24 lg:col-span-3 lg:py-32",
        className
      )}
      {...props}
    >
      <div className="inline-flex items-center justify-center w-16 h-16 mx-auto mb-6 rounded-lg bg-slate-100 dark:bg-slate-800">
        {icon || <Sunrise className="h-8 w-8 text-slate-400 dark:text-slate-500" />}
      </div>

      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
        {title}
      </h2>

      {description && (
        <p className="text-slate-500 dark:text-slate-400 mb-8">
          {description}
        </p>
      )}

      {actionLabel && actionHref && (
        <div className="mt-8">
          <a
            href={actionHref}
            className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            <svg
              className="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
            {actionLabel}
          </a>
        </div>
      )}
    </div>
  );
}

export function EmptyApplicationsState({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "col-span-1 text-center py-12 px-4",
        "sm:col-span-2 sm:py-20 lg:col-span-3 lg:py-28",
        "border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl",
        className
      )}
      {...props}
    >
      <div className="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center flex-shrink-0 bg-slate-100 dark:bg-slate-800">
        <FolderDownload className="h-8 w-8 text-slate-400 dark:text-slate-500" />
      </div>

      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
        No Applications Found
      </h2>
      <p className="text-slate-500 dark:text-slate-400 mb-6">
        Start by applying for a government service or uploading documents to see them here.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <a
          href="/apply"
          className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          <svg
            className="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
          Apply for a Service
        </a>
        <a
          href="/documents"
          className="inline-flex items-center gap-2 rounded-md border border-slate-400 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:border-slate-500 dark:hover:border-slate-600 focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
        >
          <svg
            className="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="3" y1="3" x2="21" y2="21" />
            <line x1="21" y1="3" x2="3" y2="21" />
          </svg>
          Manage Documents
        </a>
      </div>
    </div>
  );
}

export function EmptyGrievancesState({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "col-span-1 text-center py-12 px-4",
        "sm:col-span-2 sm:py-20 lg:col-span-3 lg:py-28",
        "border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl",
        className
      )}
      {...props}
    >
      <div className="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center flex-shrink-0 bg-slate-100 dark:bg-slate-800">
        <AlertCircle className="h-8 w-8 text-slate-400 dark:text-slate-500" />
      </div>

      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
        No Grievances Yet
      </h2>
      <p className="text-slate-500 dark:text-slate-400 mb-6">
        Report an issue to see it tracked here.
      </p>

      <a
        href="/grievance/new"
        className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      >
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="5" y1="12" x2="19" y2="12" />
          <polyline points="12 5 19 12 12 19" />
        </svg>
        Report a New Grievance
      </a>
    </div>
  );
}

export function EmptyDocumentsState({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "col-span-1 text-center py-12 px-4",
        "sm:col-span-2 sm:py-20 lg:col-span-3 lg:py-28",
        "border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-2xl",
        className
      )}
      {...props}
    >
      <div className="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center flex-shrink-0 bg-slate-100 dark:bg-slate-800">
        <FolderDownload className="h-8 w-8 text-slate-400 dark:text-slate-500" />
      </div>

      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
        No Documents Found
      </h2>
      <p className="text-slate-500 dark:text-slate-400 mb-6">
        Upload your government documents to get started.
      </p>

      <a
        href="/documents/upload"
        className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      >
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="5" y1="12" x2="19" y2="12" />
          <polyline points="12 5 19 12 12 19" />
        </svg>
        Upload Document
      </a>
    </div>
  );
}