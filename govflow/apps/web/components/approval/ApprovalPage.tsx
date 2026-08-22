"use client";

import { useState, useCallback } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SuccessModal } from "./SuccessModal";
import { mockApprovalRequest, submitApproval } from "@/lib/mock-data";
import { formatDate } from "@/lib/utils";
import type { ApprovalResult } from "@/lib/api/types";
import {
  Building2,
  Globe,
  User,
  FileText,
  ClipboardList,
  Pencil,
  X,
  Send,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  ShieldCheck,
  Loader2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

export function ApprovalPage() {
  const request = mockApprovalRequest;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successModalOpen, setSuccessModalOpen] = useState(false);
  const [approvalResult, setApprovalResult] =
    useState<ApprovalResult | null>(null);
  const [expandedSections, setExpandedSections] = useState<
    Record<string, boolean>
  >({
    service: true,
    department: true,
    portal: true,
    applicant: true,
    documents: true,
    form: true,
  });

  const toggleSection = (key: string) => {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleApprove = useCallback(async () => {
    setIsSubmitting(true);
    try {
      const result = await submitApproval(request.id);
      setApprovalResult(result);
      setSuccessModalOpen(true);
    } finally {
      setIsSubmitting(false);
    }
  }, [request.id]);

  const handleCancel = useCallback(() => {
    // Placeholder — would navigate back or show confirmation
  }, []);

  const handleEdit = useCallback(() => {
    // Placeholder — would enable edit mode or navigate to edit form
  }, []);

  const verifiedCount = request.documents.filter(
    (d) => d.status === "verified"
  ).length;
  const allDocsVerified = verifiedCount === request.documents.length;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Review & Approve
        </h1>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Review your application details before final submission
        </p>
      </div>

      {/* Security notice */}
      <div className="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 dark:border-green-900/30 dark:bg-green-950/20 dark:text-green-400">
        <ShieldCheck className="h-4 w-4 flex-shrink-0" />
        <span>
          Your data is encrypted end-to-end. No information is shared until you
          approve.
        </span>
      </div>

      {/* ─── Service ─── */}
      <Section
        title="Service"
        icon={<ClipboardList className="h-4 w-4" />}
        expanded={expandedSections.service}
        onToggle={() => toggleSection("service")}
        badge={
          <Badge variant="info" className="text-xs">
            Pending Approval
          </Badge>
        }
      >
        <div className="space-y-3">
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-white">
              {request.service}
            </p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
              {request.serviceDescription}
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Created {formatDate(request.createdAt)}
            </span>
            <span>ID: {request.id}</span>
          </div>
        </div>
      </Section>

      {/* ─── Department ─── */}
      <Section
        title="Department"
        icon={<Building2 className="h-4 w-4" />}
        expanded={expandedSections.department}
        onToggle={() => toggleSection("department")}
      >
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <InfoRow label="Department" value={request.department.name} />
          <InfoRow label="Code" value={request.department.code} />
          <InfoRow label="Jurisdiction" value={request.department.jurisdiction} />
          <InfoRow
            label="Contact"
            value={
              <span className="flex items-center gap-1">
                <Mail className="h-3 w-3" />
                {request.department.contactEmail}
              </span>
            }
          />
          <InfoRow
            label="Phone"
            value={
              <span className="flex items-center gap-1">
                <Phone className="h-3 w-3" />
                {request.department.contactPhone}
              </span>
            }
          />
        </div>
      </Section>

      {/* ─── Official Portal ─── */}
      <Section
        title="Official Portal"
        icon={<Globe className="h-4 w-4" />}
        expanded={expandedSections.portal}
        onToggle={() => toggleSection("portal")}
        badge={
          <Badge variant="success" className="text-xs gap-1">
            <CheckCircle2 className="h-3 w-3" />
            Verified
          </Badge>
        }
      >
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                {request.portal.name}
              </p>
              <p className="mt-0.5 flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                <Globe className="h-3 w-3" />
                {request.portal.url}
              </p>
            </div>
            <Button variant="ghost" size="sm" className="gap-1" asChild>
              <a
                href={request.portal.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="h-3 w-3" />
                Visit
              </a>
            </Button>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Last verified: {formatDate(request.portal.lastVerified)}
          </p>
        </div>
      </Section>

      {/* ─── Applicant ─── */}
      <Section
        title="Applicant"
        icon={<User className="h-4 w-4" />}
        expanded={expandedSections.applicant}
        onToggle={() => toggleSection("applicant")}
      >
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <InfoRow label="Full Name" value={request.applicant.name} />
          <InfoRow label="Date of Birth" value={formatDate(request.applicant.dateOfBirth)} />
          <InfoRow label="Gender" value={request.applicant.gender} />
          <InfoRow
            label="Aadhaar"
            value={`XXXX XXXX ${request.applicant.aadhaarLast4}`}
          />
          <InfoRow
            label="Email"
            value={
              <span className="flex items-center gap-1">
                <Mail className="h-3 w-3" />
                {request.applicant.email}
              </span>
            }
          />
          <InfoRow
            label="Phone"
            value={
              <span className="flex items-center gap-1">
                <Phone className="h-3 w-3" />
                {request.applicant.phone}
              </span>
            }
          />
          <div className="sm:col-span-2">
            <InfoRow
              label="Address"
              value={
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {request.applicant.address}
                </span>
              }
            />
          </div>
        </div>
      </Section>

      {/* ─── Documents ─── */}
      <Section
        title="Documents"
        icon={<FileText className="h-4 w-4" />}
        expanded={expandedSections.documents}
        onToggle={() => toggleSection("documents")}
        badge={
          allDocsVerified ? (
            <Badge variant="success" className="text-xs gap-1">
              <CheckCircle2 className="h-3 w-3" />
              All Verified
            </Badge>
          ) : (
            <Badge variant="warning" className="text-xs gap-1">
              <AlertTriangle className="h-3 w-3" />
              {request.documents.length - verifiedCount} Need Review
            </Badge>
          )
        }
      >
        <div className="space-y-2">
          {request.documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2.5 dark:border-slate-800 dark:bg-slate-900"
            >
              <FileText className="h-4 w-4 flex-shrink-0 text-slate-400" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
                  {doc.name}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {doc.type} &middot; {(doc.size / (1024 * 1024)).toFixed(1)} MB
                </p>
              </div>
              <DocumentStatusBadge status={doc.status} />
            </div>
          ))}
        </div>
      </Section>

      {/* ─── Form Summary ─── */}
      <Section
        title="Form Summary"
        icon={<ClipboardList className="h-4 w-4" />}
        expanded={expandedSections.form}
        onToggle={() => toggleSection("form")}
      >
        <div className="space-y-0 divide-y divide-slate-200 dark:divide-slate-800">
          {request.formFields.map((field) => (
            <div
              key={field.label}
              className="flex items-center justify-between py-2.5"
            >
              <span className="text-sm text-slate-500 dark:text-slate-400">
                {field.label}
              </span>
              <span className="text-sm font-medium text-slate-900 dark:text-white">
                {field.value}
              </span>
            </div>
          ))}
        </div>
      </Section>

      {/* ─── Action Bar ─── */}
      <div className="sticky bottom-0 rounded-xl border border-slate-200 bg-white p-4 shadow-lg dark:border-slate-800 dark:bg-slate-950">
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleEdit}
              className="gap-1"
            >
              <Pencil className="h-4 w-4" />
              Edit
            </Button>
            <Button
              variant="ghost"
              onClick={handleCancel}
              className="gap-1 text-slate-600 hover:text-red-600 dark:text-slate-400"
            >
              <X className="h-4 w-4" />
              Cancel
            </Button>
          </div>

          <Button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="gap-2 bg-green-600 text-white hover:bg-green-700 focus:ring-green-500"
            size="lg"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Approve & Submit
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Success Modal */}
      <SuccessModal
        open={successModalOpen}
        onOpenChange={setSuccessModalOpen}
        result={approvalResult}
      />
    </div>
  );
}

// ─── Helper sub-components ─────────────────────────────────────────────────

function Section({
  title,
  icon,
  expanded,
  onToggle,
  badge,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  expanded: boolean;
  onToggle: () => void;
  badge?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between p-4 text-left"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-slate-500 dark:text-slate-400">{icon}</span>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
            {title}
          </h2>
          {badge}
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-slate-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-400" />
        )}
      </button>
      {expanded && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  );
}

function InfoRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div>
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-0.5 text-sm font-medium text-slate-900 dark:text-white">
        {value}
      </p>
    </div>
  );
}

function DocumentStatusBadge({
  status,
}: {
  status: "verified" | "needs_review" | "rejected";
}) {
  const config = {
    verified: {
      label: "Verified",
      classes:
        "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
      icon: CheckCircle2,
    },
    needs_review: {
      label: "Needs Review",
      classes:
        "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
      icon: AlertTriangle,
    },
    rejected: {
      label: "Rejected",
      classes: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
      icon: AlertTriangle,
    },
  } as const;

  const c = config[status];
  const Icon = c.icon;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${c.classes}`}
    >
      <Icon className="h-3 w-3" />
      {c.label}
    </span>
  );
}
