"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, FileText, Clock, ArrowRight } from "lucide-react";
import type { ServiceOption } from "../types";

interface ServiceStepProps {
  services: ServiceOption[];
  selectedService?: ServiceOption;
  onSelect: (service: ServiceOption) => void;
  className?: string;
}

export function ServiceStep({
  services,
  selectedService,
  onSelect,
  className,
}: ServiceStepProps) {
  return (
    <div className={cn("p-4 sm:p-6 space-y-4", className)}>
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          Select a Service
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Choose the government service you need help with
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {services.map((service) => {
          const isSelected = selectedService?.id === service.id;
          return (
            <Card
              key={service.id}
              className={cn(
                "cursor-pointer transition-all hover:shadow-md",
                isSelected
                  ? "border-gov-blue ring-2 ring-gov-blue/20"
                  : "hover:border-slate-300 dark:hover:border-slate-600"
              )}
              onClick={() => onSelect(service)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div
                      className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-lg shrink-0",
                        isSelected
                          ? "bg-gov-blue text-white"
                          : "bg-slate-100 dark:bg-slate-800"
                      )}
                    >
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900 dark:text-white">
                        {service.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {service.department}
                      </p>
                      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 line-clamp-2">
                        {service.description}
                      </p>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gov-blue">
                      <Check className="h-4 w-4 text-white" />
                    </div>
                  )}
                </div>
                <div className="mt-3 flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>{service.estimatedTime}</span>
                  </div>
                  <Badge variant="secondary" className="text-[10px]">
                    {service.category}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
