import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, TrendingUp } from "lucide-react";

interface ConfidenceCardProps {
  value: number;
  label?: string;
  className?: string;
}

export function ConfidenceCard({
  value,
  label = "Agent Confidence",
  className,
}: ConfidenceCardProps) {
  const getVariant = () => {
    if (value >= 80) return "success";
    if (value >= 50) return "warning";
    return "destructive";
  };

  const getColor = () => {
    if (value >= 80) return "text-green-600 dark:text-green-400";
    if (value >= 50) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
            <ShieldCheck className="h-4 w-4 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
            {label}
          </p>
        </div>
        <Badge variant={getVariant() as "success" | "warning" | "destructive"}>
          <TrendingUp className="mr-1 h-3 w-3" />
          {value}%
        </Badge>
      </div>
      <div className="mt-3">
        <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
          <div
            className={cn(
              "h-2 rounded-full transition-all duration-500",
              value >= 80
                ? "bg-green-500"
                : value >= 50
                ? "bg-yellow-500"
                : "bg-red-500"
            )}
            style={{ width: `${value}%` }}
          />
        </div>
      </div>
    </div>
  );
}
