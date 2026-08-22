import { Lightbulb } from "lucide-react";
import { mockGovernmentTips } from "@/lib/mock-data";

export function GovernmentTips() {
  return (
    <section className="w-full max-w-4xl mx-auto">
      <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-4">
        Government Tips
      </h2>
      <div className="card">
        <div className="mb-4 flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          <h3 className="font-semibold text-slate-900 dark:text-white">
            Tips for a smooth application
          </h3>
        </div>
        <ul className="space-y-4">
          {mockGovernmentTips.map((tip) => (
            <li key={tip.id} className="flex items-start gap-3">
              <span className="text-xl" aria-hidden>
                {tip.icon}
              </span>
              <div>
                <p className="font-medium text-slate-800 dark:text-slate-200">
                  {tip.title}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {tip.description}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}