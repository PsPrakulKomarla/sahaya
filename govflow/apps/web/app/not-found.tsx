import { GlobalErrorOverlay } from "@/components/ui/ErrorBoundary";
import { useState } from "react";

export const notFound = () => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 mx-auto mb-8 rounded-full bg-slate-100 dark:bg-slate-800">
          <svg
            className="h-10 w-10 text-slate-400 dark:text-slate-500"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="12" y1="1" x2="12" y2="23" />
            <line x1="5" y1="11" x2="19" y2="11" />
            <line x1="5" y1="17" x2="19" y2="17" />
            <line x1="9" y1="21" x2="15" y2="21" />
            <circle cx="12" cy="12" r="10" />
          </svg>
        </div>

        <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
          404 - Page Not Found
        </h1>

        <p className="text-slate-600 dark:text-slate-400 mb-8">
          The page you're looking for doesn't exist.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/"
            className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-5 py-3 text-sm font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
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
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
            Go to Home
          </a>
          <a
            href="/applications"
            className="inline-flex items-center gap-2 rounded-md border border-slate-400 px-5 py-3 text-sm font-medium text-slate-700 dark:text-slate-300 hover:border-slate-500 dark:hover:border-slate-600 focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
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
              <line x1="3" y1="3" x2="21" y2="21" />
              <line x1="21" y1="3" x2="3" y2="21" />
            </svg>
            View Applications
          </a>
        </div>
      </div>
    </div>
  );
};