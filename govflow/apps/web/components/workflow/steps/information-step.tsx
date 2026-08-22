"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { FormSection, FormField } from "../types";

interface FormFieldInputProps {
  field: FormField;
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
}

function FormFieldInput({ field, value, onChange, className }: FormFieldInputProps) {
  const fieldValue = value ?? field.value ?? "";

  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={field.id} className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {field.label}
        {field.required && <span className="ml-1 text-red-500">*</span>}
      </Label>
      {field.type === "text" || field.type === "email" || field.type === "phone" || field.type === "date" ? (
        <Input
          id={field.id}
          type={field.type === "phone" ? "tel" : field.type}
          placeholder={field.placeholder}
          value={fieldValue}
          onChange={(e) => onChange?.(e.target.value)}
          required={field.required}
        />
      ) : field.type === "select" && field.options ? (
        <Select value={fieldValue} onValueChange={onChange}>
          <SelectTrigger>
            <SelectValue placeholder={field.placeholder || `Select ${field.label}`} />
          </SelectTrigger>
          <SelectContent>
            {field.options.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ) : field.type === "textarea" ? (
        <Textarea
          id={field.id}
          placeholder={field.placeholder}
          value={fieldValue}
          onChange={(e) => onChange?.(e.target.value)}
          required={field.required}
          rows={4}
        />
      ) : (
        <Input
          id={field.id}
          placeholder={field.placeholder}
          value={fieldValue}
          onChange={(e) => onChange?.(e.target.value)}
          required={field.required}
        />
      )}
      {field.validation?.message && (
        <p className="text-xs text-red-500">{field.validation.message}</p>
      )}
    </div>
  );
}

interface InformationStepProps {
  sections: FormSection[];
  formData: Record<string, string>;
  onFieldChange: (fieldId: string, value: string) => void;
  className?: string;
}

export function InformationStep({
  sections,
  formData,
  onFieldChange,
  className,
}: InformationStepProps) {
  return (
    <div className={cn("p-4 sm:p-6 space-y-6", className)}>
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          Applicant Information
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Provide the required details for your application
        </p>
      </div>

      {sections.map((section) => (
        <Card key={section.id}>
          <CardHeader className="pb-4">
            <CardTitle className="text-base">{section.title}</CardTitle>
            {section.description && (
              <CardDescription>{section.description}</CardDescription>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {section.fields.map((field) => (
                <FormFieldInput
                  key={field.id}
                  field={field}
                  value={formData[field.id]}
                  onChange={(value) => onFieldChange(field.id, value)}
                  className={field.type === "textarea" ? "sm:col-span-2" : ""}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
