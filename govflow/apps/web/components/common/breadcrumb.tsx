"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items?: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  const pathname = usePathname();

  const generatedItems = React.useMemo(() => {
    if (items) return items;

    const segments = pathname.split("/").filter(Boolean);
    const result: BreadcrumbItem[] = [{ label: "Home", href: "/" }];

    let currentPath = "";
    segments.forEach((segment) => {
      currentPath += `/${segment}`;
      result.push({
        label: segment.charAt(0).toUpperCase() + segment.slice(1),
        href: currentPath,
      });
    });

    return result;
  }, [pathname, items]);

  return (
    <nav
      aria-label="Breadcrumb"
      className={cn("flex items-center space-x-1 text-sm", className)}
    >
      <ol className="flex items-center space-x-1">
        {generatedItems.map((item, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="mx-1 h-4 w-4 text-slate-400" />
            )}
            {item.href && index < generatedItems.length - 1 ? (
              <Link
                href={item.href}
                className="flex items-center gap-1 text-slate-600 hover:text-gov-blue dark:text-slate-400 dark:hover:text-gov-blue-light"
              >
                {index === 0 && <Home className="h-4 w-4" />}
                {item.label}
              </Link>
            ) : (
              <span className="flex items-center gap-1 font-medium text-slate-900 dark:text-white">
                {index === 0 && <Home className="h-4 w-4" />}
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
