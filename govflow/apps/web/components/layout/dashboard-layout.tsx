"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Sidebar } from "./sidebar";
import { Header } from "./header";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Sidebar - Desktop */}
      <div className="hidden md:block">
        <Sidebar
          isCollapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - Mobile */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 md:hidden transition-transform duration-300",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <Sidebar
          isCollapsed={false}
          onToggle={() => setMobileMenuOpen(false)}
        />
      </div>

      {/* Main Content */}
      <div
        className={cn(
          "transition-all duration-300",
          sidebarCollapsed ? "md:ml-[68px]" : "md:ml-64"
        )}
      >
        <Header onMenuClick={() => setMobileMenuOpen(true)} />

        <main className="min-h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
