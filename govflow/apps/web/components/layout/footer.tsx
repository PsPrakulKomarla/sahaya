import Link from "next/link";
import { Shield } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 py-8 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-gov-blue" />
              <span className="text-lg font-bold text-slate-900 dark:text-white">
                GovFlow AI
              </span>
            </Link>
            <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">
              Universal government service browser agent. Making government
              services accessible to every citizen.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Services
            </h3>
            <ul className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li>
                <Link href="/apply" className="hover:text-gov-blue">
                  Apply for Service
                </Link>
              </li>
              <li>
                <Link href="/documents" className="hover:text-gov-blue">
                  Document Vault
                </Link>
              </li>
              <li>
                <Link href="/applications" className="hover:text-gov-blue">
                  Track Applications
                </Link>
              </li>
              <li>
                <Link href="/grievance" className="hover:text-gov-blue">
                  Raise Grievance
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Languages
            </h3>
            <ul className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li>English</li>
              <li>Kannada</li>
              <li>Hindi</li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Legal
            </h3>
            <ul className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li>
                <Link href="/privacy" className="hover:text-gov-blue">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-gov-blue">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/security" className="hover:text-gov-blue">
                  Security
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-200 py-6 text-center text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400">
          &copy; {new Date().getFullYear()} GovFlow AI. Not affiliated with any
          government agency.
        </div>
      </div>
    </footer>
  );
}
