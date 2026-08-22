import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Shield } from "lucide-react";

interface AIMessageProps {
  content: string;
  timestamp?: string;
  className?: string;
}

export function AIMessage({ content, timestamp, className }: AIMessageProps) {
  return (
    <div className={cn("flex gap-3", className)}>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="bg-gov-blue text-white">
          <Shield className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>
      <div className="flex flex-col gap-1 max-w-[80%] sm:max-w-[70%]">
        <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100">
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
        {timestamp && (
          <span className="text-xs text-slate-400 dark:text-slate-500">
            {timestamp}
          </span>
        )}
      </div>
    </div>
  );
}
