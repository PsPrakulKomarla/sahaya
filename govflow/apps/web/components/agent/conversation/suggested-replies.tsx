"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

interface SuggestedRepliesProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
  className?: string;
}

export function SuggestedReplies({
  suggestions,
  onSelect,
  className,
}: SuggestedRepliesProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {suggestions.map((suggestion, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          className="rounded-full border-slate-200 bg-white text-slate-700 hover:border-gov-blue hover:text-gov-blue dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-gov-blue-light dark:hover:text-gov-blue-light"
          onClick={() => onSelect(suggestion)}
        >
          {suggestion}
          <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      ))}
    </div>
  );
}
