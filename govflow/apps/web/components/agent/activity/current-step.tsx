import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Activity, ArrowRight } from "lucide-react";

interface CurrentStepProps {
  step: string;
  description?: string;
  stepNumber?: number;
  totalSteps?: number;
  className?: string;
}

export function CurrentStep({
  step,
  description,
  stepNumber,
  totalSteps,
  className,
}: CurrentStepProps) {
  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
            <Activity className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Current Step
            </p>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">
              {step}
            </p>
          </div>
        </div>
        {stepNumber && totalSteps && (
          <Badge variant="outline">
            {stepNumber}/{totalSteps}
          </Badge>
        )}
      </div>
      {description && (
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          {description}
        </p>
      )}
    </div>
  );
}
