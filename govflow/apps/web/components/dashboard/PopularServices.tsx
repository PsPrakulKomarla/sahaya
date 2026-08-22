import Link from "next/link";
import { mockPopularServices } from "@/lib/mock-data";

export function PopularServices() {
  return (
    <section className="w-full max-w-4xl mx-auto">
      <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-4">
        Popular Services
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {mockPopularServices.map((service) => (
          <Link
            key={service.id}
            href={service.href ?? "/apply"}
            className="card flex items-center gap-4 group transition-shadow hover:shadow-md"
          >
            <span className="text-3xl" aria-hidden>
              {service.icon}
            </span>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-primary-600 transition-colors">
                {service.name}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {service.category}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}