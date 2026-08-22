import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  Clock,
  XCircle,
  Circle,
  Loader2,
} from "lucide-react";
import type { TimelineEvent, TimelineStatus } from "./types";

interface ApplicationTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

const statusIcon: Record<TimelineStatus, React.ElementType> = {
  draft: Circle,
  submitted: CheckCircle,
  under_review: Clock,
  processing: Loader2,
  completed: CheckCircle,
  rejected: XCircle,
};

const statusColor: Record<TimelineStatus, string> = {
  draft: "text-slate-400",
  submitted: "text-blue-500",
  under_review: "text-yellow-500",
  processing: "text-orange-500",
  completed: "text-green-500",
  rejected: "text-red-500",
};

const statusBg: Record<TimelineStatus, string> = {
  draft: "bg-slate-100 dark:bg-slate-800",
  submitted: "bg-blue-100 dark:bg-blue-900/30",
  under_review: "bg-yellow-100 dark:bg-yellow-900/30",
  processing: "bg-orange-100 dark:bg-orange-900/30",
  completed: "bg-green-100 dark:bg-green-900/30",
  rejected: "bg-red-100 dark:bg-red-900/30",
};

const statusBadge: Record<TimelineStatus, "default" | "success" | "destructive" | "warning" | "info" | "outline"> = {
  draft: "outline",
  submitted: "info",
  under_review: "warning",
  processing: "warning",
  completed: "success",
  rejected: "destructive",
};

export function ApplicationTimeline({
  events,
  className,
}: ApplicationTimelineProps) {
  return (
    <div className={cn("relative", className)}>
      {events.map((event, index) => {
        const Icon = statusIcon[event.status];
        const isLast = index === events.length - 1;

        return (
          <div key={event.id} className="flex gap-4">
            {/* Line + Icon */}
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full border-2 shrink-0",
                  event.completed
                    ? event.status === "rejected"
                      ? "border-red-500 bg-red-50 dark:bg-red-900/20"
                      : "border-green-500 bg-green-50 dark:bg-green-900/20"
                    : "border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
                )}
              >
                <Icon
                  className={cn(
                    "h-5 w-5",
                    event.completed
                      ? event.status === "rejected"
                        ? "text-red-500"
                        : "text-green-500"
                      : "text-slate-300 dark:text-slate-600",
                    event.status === "processing" && event.completed && "animate-spin"
                  )}
                />
              </div>
              {!isLast && (
                <div
                  className={cn(
                    "w-0.5 flex-1 min-h-[2rem]",
                    event.completed
                      ? event.status === "rejected"
                        ? "bg-red-300 dark:bg-red-700"
                        : "bg-green-300 dark:bg-green-700"
                      : "bg-slate-200 dark:bg-slate-700"
                  )}
                />
              )}
            </div>

            {/* Content */}
            <div className={cn("pb-8", isLast && "pb-0")}>
              <div className="flex items-center gap-2">
                <p
                  className={cn(
                    "text-sm font-medium",
                    event.completed
                      ? "text-slate-900 dark:text-white"
                      : "text-slate-400 dark:text-slate-500"
                  )}
                >
                  {event.label}
                </p>
                <Badge variant={statusBadge[event.status]} className="text-[10px]">
                  {event.status.replace("_", " ")}
                </Badge>
              </div>
              {event.description && (
                <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                  {event.description}
                </p>
              )}
              {event.timestamp && (
                <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
                  {new Date(event.timestamp).toLocaleString("en-IN", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                    hour: "numeric",
                    minute: "2-digit",
                  })}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
