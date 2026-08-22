"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, X } from "lucide-react";
import type { ApplicationStatus } from "./types";

type FilterStatus = ApplicationStatus | "all";

interface ApplicationFiltersProps {
  activeFilter: FilterStatus;
  searchQuery: string;
  onFilterChange: (filter: FilterStatus) => void;
  onSearchChange: (query: string) => void;
  counts: Record<FilterStatus, number>;
  className?: string;
}

const filterTabs: { value: FilterStatus; label: string }[] = [
  { value: "all", label: "All" },
  { value: "draft", label: "Draft" },
  { value: "submitted", label: "Submitted" },
  { value: "processing", label: "Processing" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
];

export function ApplicationFilters({
  activeFilter,
  searchQuery,
  onFilterChange,
  onSearchChange,
  counts,
  className,
}: ApplicationFiltersProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <Input
          type="search"
          placeholder="Search by service, reference number..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10 pr-10"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {filterTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => onFilterChange(tab.value)}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
              activeFilter === tab.value
                ? "bg-gov-blue text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700"
            )}
          >
            {tab.label}
            <Badge
              variant={activeFilter === tab.value ? "secondary" : "outline"}
              className={cn(
                "ml-0.5 h-5 min-w-5 px-1 text-[10px]",
                activeFilter === tab.value &&
                  "bg-white/20 text-white border-white/30"
              )}
            >
              {counts[tab.value]}
            </Badge>
          </button>
        ))}
      </div>
    </div>
  );
}
