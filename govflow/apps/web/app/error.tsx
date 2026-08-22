"use client";

import { GlobalErrorOverlay } from "@/components/ui/ErrorBoundary";
import { useState } from "react";

export default function Error({
  error,
  reset,
  ...props
}: {
  error: Error;
  reset?: () => void;
  className?: string;
}) {
  const [showOverlay, setShowOverlay] = useState(false);

  return (
    <div className={cn("min-h-screen bg-slate-50 dark:bg-slate-900", className)}>
      <div className="container mx-auto px-4 py-12">
        <GlobalErrorOverlay
          error={error}
          resetError={reset}
          className="mt-16"
        />
      </div>
    </div>
  );
}