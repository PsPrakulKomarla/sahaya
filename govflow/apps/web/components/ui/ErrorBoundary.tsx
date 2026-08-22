"use client";

import { useEffect } from "react";
import useSWR from "swr";
import useSwrInfinite from "swr/infinite";

// Error boundary component for catching render errors
export class ErrorBoundary extends React.Component<{
  hasError: boolean;
  error?: Error;
  fallback?: React.ReactNode;
}> {
  constructor(props: {
    hasError: boolean;
    error?: Error;
    fallback?: React.ReactNode;
  }) {
    super(props);
    this.state = { hasError: props.hasError, error: props.error };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // In production, you could log this to an error tracking service
    console.error("Error caught by boundary:", error, info);
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return this.props.fallback;
  }
}

// Global error overlay component
export function GlobalErrorOverlay({
  error,
  resetError,
  ...props
}: {
  error?: Error;
  resetError?: () => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md",
        className
      )}
    >
      <div className="bg-white dark:bg-slate-900 rounded-xl p-8 max-w-md w-full text-center shadow-2xl transform scale-95">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full flex items-center justify-center bg-red-100 dark:bg-red-900/20">
          <svg
            className="h-8 w-8 text-red-600"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="18" y2="18" />
            <line x1="6" y1="6" x2="18" y2="6" />
            <line x1="6" y1="18" x2="18" y2="18" />
          </svg>
        </div>

        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
          Something went wrong
        </h2>

        <p className="text-slate-600 dark:text-slate-400 mb-8">
          We encountered an unexpected error. Our team has been notified and we'll
          fix this shortly.
        </p>

        {resetError && (
          <button
            onClick={resetError}
            className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            <svg
              className="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="18" y2="18" />
              <line x1="6" y1="6" x2="18" y2="6" />
              <line x1="6" y1="18" x2="18" y2="18" />
            </svg>
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}