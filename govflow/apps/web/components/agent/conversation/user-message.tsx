import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface UserMessageProps {
  content: string;
  timestamp?: string;
  className?: string;
}

export function UserMessage({ content, timestamp, className }: UserMessageProps) {
  return (
    <div className={cn("flex gap-3 justify-end", className)}>
      <div className="flex flex-col items-end gap-1 max-w-[80%] sm:max-w-[70%]">
        <div className="rounded-2xl rounded-br-md bg-gov-blue px-4 py-3 text-sm text-white">
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
        {timestamp && (
          <span className="text-xs text-slate-400 dark:text-slate-500">
            {timestamp}
          </span>
        )}
      </div>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          You
        </AvatarFallback>
      </Avatar>
    </div>
  );
}
