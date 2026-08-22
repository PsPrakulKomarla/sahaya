"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Globe,
  Lock,
  RefreshCw,
  Maximize2,
  Minimize2,
  Loader2,
  Monitor,
} from "lucide-react";

interface BrowserPreviewProps {
  url?: string;
  pageTitle?: string;
  isLoading?: boolean;
  screenshotUrl?: string;
  className?: string;
}

export function BrowserPreview({
  url = "https://service.karnataka.gov.in",
  pageTitle = "Karnataka e-Service Portal",
  isLoading = false,
  screenshotUrl,
  className,
}: BrowserPreviewProps) {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const isSecure = url.startsWith("https://");

  return (
    <div
      className={cn(
        "rounded-xl border border-slate-200 bg-white overflow-hidden dark:border-slate-800 dark:bg-slate-950",
        isExpanded ? "fixed inset-4 z-50" : "",
        className
      )}
    >
      {/* Browser Header */}
      <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-3 py-2 dark:border-slate-800 dark:bg-slate-900">
        {/* Traffic Lights */}
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 rounded-full bg-red-400" />
          <div className="h-3 w-3 rounded-full bg-yellow-400" />
          <div className="h-3 w-3 rounded-full bg-green-400" />
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center gap-1 ml-2">
          <Button variant="ghost" size="icon" className="h-6 w-6" disabled>
            <RefreshCw className={cn("h-3 w-3", isLoading && "animate-spin")} />
          </Button>
        </div>

        {/* URL Bar */}
        <div className="flex-1 flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-1 dark:border-slate-700 dark:bg-slate-800">
          {isLoading ? (
            <Loader2 className="h-3 w-3 text-slate-400 animate-spin" />
          ) : isSecure ? (
            <Lock className="h-3 w-3 text-green-500" />
          ) : (
            <Globe className="h-3 w-3 text-slate-400" />
          )}
          <span className="text-xs text-slate-600 dark:text-slate-300 truncate">
            {url}
          </span>
        </div>

        {/* Page Label */}
        <Badge variant="secondary" className="text-[10px] hidden sm:inline-flex">
          {pageTitle}
        </Badge>

        {/* Expand/Collapse */}
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <Minimize2 className="h-3 w-3" />
          ) : (
            <Maximize2 className="h-3 w-3" />
          )}
        </Button>
      </div>

      {/* Screenshot Area */}
      <div className="relative aspect-video bg-slate-100 dark:bg-slate-900">
        {screenshotUrl ? (
          <img
            src={screenshotUrl}
            alt={pageTitle}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            {isLoading ? (
              <>
                <Loader2 className="h-10 w-10 text-gov-blue animate-spin" />
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Navigating to portal...
                </p>
              </>
            ) : (
              <>
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-200 dark:bg-slate-800">
                  <Monitor className="h-8 w-8 text-slate-400" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                    Browser Preview
                  </p>
                  <p className="text-xs text-slate-400 dark:text-slate-500">
                    Screenshots will stream here during agent activity
                  </p>
                </div>
              </>
            )}
          </div>
        )}

        {/* Overlay indicator when agent is active */}
        {isLoading && (
          <div className="absolute top-3 left-3">
            <Badge variant="info" className="gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
              Agent Active
            </Badge>
          </div>
        )}
      </div>
    </div>
  );
}
