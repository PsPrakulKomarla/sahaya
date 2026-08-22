import { cn } from "@/lib/utils";
import { Clock, Play, Pause } from "lucide-react";

interface RuntimeCardProps {
  elapsed: string;
  isRunning?: boolean;
  className?: string;
}

export function RuntimeCard({
  elapsed,
  isRunning = true,
  className,
}: RuntimeCardProps) {
  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30">
            <Clock className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Runtime
            </p>
            <p className="text-lg font-bold text-slate-900 dark:text-white font-mono">
              {elapsed}
            </p>
          </div>
        </div>
        <div className={cn(
          "flex h-8 w-8 items-center justify-center rounded-full",
          isRunning
            ? "bg-green-100 dark:bg-green-900/30"
            : "bg-slate-100 dark:bg-slate-800"
        )}>
          {isRunning ? (
            <Play className="h-4 w-4 text-green-600 dark:text-green-400" />
          ) : (
            <Pause className="h-4 w-4 text-slate-400" />
          )}
        </div>
      </div>
    </div>
  );
}
