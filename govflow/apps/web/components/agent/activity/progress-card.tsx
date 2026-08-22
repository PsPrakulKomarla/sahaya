import { cn } from "@/lib/utils";

interface ProgressCardProps {
  label: string;
  value: number;
  maxValue?: number;
  unit?: string;
  color?: string;
  className?: string;
}

export function ProgressCard({
  label,
  value,
  maxValue = 100,
  unit = "%",
  color = "bg-gov-blue",
  className,
}: ProgressCardProps) {
  const percentage = Math.min((value / maxValue) * 100, 100);

  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950", className)}>
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
          {label}
        </p>
        <span className="text-sm font-bold text-slate-900 dark:text-white">
          {value}{unit}
        </span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className={cn("h-2 rounded-full transition-all duration-500", color)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
