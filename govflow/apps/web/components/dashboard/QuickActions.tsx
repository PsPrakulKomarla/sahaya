import Link from "next/link";
import {
  AlertCircle,
  ClipboardList,
  FileText,
  Pencil,
  Search,
} from "lucide-react";

const QUICK_ACTIONS = [
  { label: "Apply Service", icon: FileText, href: "/apply" },
    { label: "Update Record", icon: Pencil, href: "/update" },
  { label: "Track Application", icon: Search, href: "/applications" },
  { label: "Raise Grievance", icon: AlertCircle, href: "/grievance" },
] as const;

export function QuickActions() {
  return (
    <section className="w-full max-w-4xl mx-auto">
      <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-4">
        Quick Actions
      </h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {QUICK_ACTIONS.map((action) => (
          <Link
            key={action.label}
            href={action.href}
            className="card text-center group transition-shadow hover:shadow-md"
          >
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-100 dark:bg-primary-900/30 transition-transform group-hover:scale-105">
                <action.icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
              </div>
              <span className="font-medium text-slate-900 dark:text-white">
                {action.label}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}