import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Globe, ExternalLink } from "lucide-react";

interface CurrentPortalProps {
  name: string;
  url: string;
  status?: "active" | "loading" | "error";
  className?: string;
}

export function CurrentPortal({
  name,
  url,
  status = "active",
  className,
}: CurrentPortalProps) {
  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gov-blue/10">
            <Globe className="h-4 w-4 text-gov-blue" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Current Portal
            </p>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">
              {name}
            </p>
          </div>
        </div>
        <Badge variant={status === "active" ? "success" : status === "loading" ? "warning" : "destructive"}>
          {status === "active" ? "Connected" : status === "loading" ? "Loading" : "Error"}
        </Badge>
      </div>
      <div className="mt-3 flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
        <span className="truncate">{url}</span>
        <ExternalLink className="h-3 w-3 shrink-0" />
      </div>
    </div>
  );
}
