"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  FileText,
  RefreshCw,
  FolderOpen,
  ClipboardList,
  AlertCircle,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  MessageSquare,
  CheckCircle,
} from "lucide-react";

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const sidebarItems = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "AI Agent",
    href: "/chat",
    icon: MessageSquare,
  },
  {
    title: "Apply Service",
    href: "/apply",
    icon: FileText,
  },
  {
    title: "Update Records",
    href: "/update",
    icon: RefreshCw,
  },
  {
    title: "Documents",
    href: "/documents",
    icon: FolderOpen,
  },
  {
    title: "Applications",
    href: "/applications",
    icon: ClipboardList,
  },
  {
    title: "Approve",
    href: "/approval",
    icon: CheckCircle,
  },
  {
    title: "Grievances",
    href: "/grievance",
    icon: AlertCircle,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 transition-all duration-300",
        isCollapsed ? "w-[68px]" : "w-64"
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center border-b border-slate-200 dark:border-slate-800 px-4">
          <Link href="/" className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-gov-blue" />
            {!isCollapsed && (
              <span className="text-xl font-bold text-slate-900 dark:text-white">
                GovFlow
              </span>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-2">
          {sidebarItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-gov-blue text-white"
                    : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800",
                  isCollapsed && "justify-center px-2"
                )}
                title={isCollapsed ? item.title : undefined}
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {!isCollapsed && <span>{item.title}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse Toggle */}
        <div className="border-t border-slate-200 dark:border-slate-800 p-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="w-full"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <ChevronLeft className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>
    </aside>
  );
}
