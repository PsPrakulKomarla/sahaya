import type { Metadata } from "next";
import Link from "next/link";
import { Globe, LogIn } from "lucide-react";

import { AIPromptBox } from "@/components/dashboard/AIPromptBox";
import { GovernmentTips } from "@/components/dashboard/GovernmentTips";
import { PopularServices } from "@/components/dashboard/PopularServices";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { RecentApplications } from "@/components/dashboard/RecentApplications";

export const metadata: Metadata = {
  title: "GovFlow — Citizen AI Dashboard",
  description:
    "Ask GovFlow what government service you need and get guided to the right form, instantly.",
};

const NAV_LINKS = [
  { label: "Apply", href: "/apply" },
  { label: "Update", href: "/update" },
  { label: "Track", href: "/applications" },
  { label: "Grievances", href: "/grievance" },
];

/**
 * Citizen AI dashboard landing page.
 *
 * This page inlines its own header/footer rather than importing the reference
 * `components/layout/header.tsx` (which depends on a `ThemeProvider`). Keeping it
 * self-contained lets the page render in jsdom tests without a provider
 * wrapper, while the reference header/footer remain untouched for the rest of
 * the app.
 */
export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <Globe className="h-6 w-6 text-blue-600" />
            <span>GovFlow</span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="nav-link hover:text-blue-600"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/login"
              className="nav-link inline-flex items-center gap-1 hover:text-blue-600"
            >
              <LogIn className="h-4 w-4" /> Sign in
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto space-y-10 px-4 py-10">
        {/* Hero */}
        <section className="text-center">
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Tell GovFlow what government service you need.
          </h1>
          <p className="text-muted mt-4 max-w-2xl text-lg">
            Apply, update, track or raise grievances using one AI agent.
          </p>
        </section>

        {/* AI prompt box (voice button + intent chips + submit). The
            placeholder useAgent hook is a no-op — no AI responses are
            generated, per the dashboard spec. */}
        <AIPromptBox />

        {/* Quick actions */}
        <QuickActions />

        {/* Recent applications + government tips */}
        <div className="grid gap-8 lg:grid-cols-2">
          <RecentApplications />
          <GovernmentTips />
        </div>

        {/* Popular services */}
        <PopularServices />
      </main>

      <footer className="border-t pt-8 text-center text-sm text-slate-500">
        <div className="flex justify-center gap-6">
          <Link href="/privacy" className="hover:text-slate-800">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-slate-800">
            Terms
          </Link>
          <Link href="/security" className="hover:text-slate-800">
            Security
          </Link>
        </div>
        <p className="mt-4">
          © {new Date().getFullYear()} GovFlow. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
