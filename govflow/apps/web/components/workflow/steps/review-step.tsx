"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  FileText,
  CheckCircle,
  Clock,
  User,
  MapPin,
  Briefcase,
} from "lucide-react";
import type { WorkflowData } from "../types";

interface ReviewFieldProps {
  label: string;
  value: string;
  className?: string;
}

function ReviewField({ label, value, className }: ReviewFieldProps) {
  return (
    <div className={cn("flex items-start justify-between gap-4", className)}>
      <span className="text-sm text-slate-500 dark:text-slate-400">{label}</span>
      <span className="text-sm font-medium text-slate-900 dark:text-white text-right">
        {value || "-"}
      </span>
    </div>
  );
}

interface ReviewSummaryProps {
  workflowData: WorkflowData;
  className?: string;
}

export function ReviewSummary({ workflowData, className }: ReviewSummaryProps) {
  const { service, eligibility, documents, formData } = workflowData;

  const verifiedDocs = documents?.filter((d) => d.status === "verified" || d.status === "uploaded") ?? [];
  const metEligibility = eligibility?.filter((e) => e.met) ?? [];

  return (
    <div className={cn("p-4 sm:p-6 space-y-6", className)}>
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          Review Your Application
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Please review all details before submitting
        </p>
      </div>

      {/* Service Details */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-gov-blue" />
            <CardTitle className="text-base">Service Details</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <ReviewField label="Service" value={service?.name ?? ""} />
          <ReviewField label="Department" value={service?.department ?? ""} />
          <ReviewField label="Estimated Time" value={service?.estimatedTime ?? ""} />
        </CardContent>
      </Card>

      {/* Eligibility */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <CardTitle className="text-base">Eligibility</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Badge variant="success">
              {metEligibility.length} criteria met
            </Badge>
            {eligibility && metEligibility.length < eligibility.length && (
              <Badge variant="warning">
                {eligibility.length - metEligibility.length} not met
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Documents */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-gov-blue" />
            <CardTitle className="text-base">Documents</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge variant="success">
              {verifiedDocs.length} documents uploaded
            </Badge>
          </div>
          {verifiedDocs.map((doc) => (
            <div key={doc.id} className="flex items-center gap-2 text-sm">
              <CheckCircle className="h-4 w-4 text-green-600 shrink-0" />
              <span className="text-slate-700 dark:text-slate-300">{doc.name}</span>
              <Badge variant="outline" className="text-[10px] ml-auto">
                {doc.status}
              </Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Personal Information */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gov-blue" />
            <CardTitle className="text-base">Personal Information</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <ReviewField label="Full Name" value={formData?.full_name ?? ""} />
          <ReviewField label="Date of Birth" value={formData?.date_of_birth ?? ""} />
          <ReviewField label="Gender" value={formData?.gender ?? ""} />
          <ReviewField label="Mobile Number" value={formData?.phone ?? ""} />
          <ReviewField label="Email" value={formData?.email ?? ""} />
        </CardContent>
      </Card>

      {/* Address */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-gov-blue" />
            <CardTitle className="text-base">Address</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <ReviewField label="House/Flat" value={formData?.house_number ?? ""} />
          <ReviewField label="Street" value={formData?.street ?? ""} />
          <ReviewField label="City" value={formData?.city ?? ""} />
          <ReviewField label="PIN Code" value={formData?.pincode ?? ""} />
          <ReviewField label="State" value={formData?.state ?? ""} />
        </CardContent>
      </Card>

      {/* Declaration */}
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
        <p className="text-sm text-slate-600 dark:text-slate-300">
          <strong>Declaration:</strong> I hereby declare that all the information provided above is true and correct to the best of my knowledge. I understand that providing false information may result in rejection of my application.
        </p>
      </div>
    </div>
  );
}
