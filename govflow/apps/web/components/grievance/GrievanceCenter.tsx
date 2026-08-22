"use client";

import { useState, useCallback } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ApplicationSelector } from "./ApplicationSelector";
import { ComplaintForm } from "./ComplaintForm";
import { SubmittedGrievances } from "./SubmittedGrievances";
import { GrievanceApprovalModal } from "./GrievanceApprovalModal";
import { mockRecentApplications, mockGrievanceTickets, submitGrievance } from "@/lib/mock-data";
import type {
  RecentApplication,
  GrievanceDraft,
  GrievanceTicket,
  GrievanceSubmitResult,
} from "@/lib/api/types";
import {
  AlertCircle,
  Clock,
  CheckCircle2,
  FileText,
} from "lucide-react";

export function GrievanceCenter() {
  const [selectedApp, setSelectedApp] = useState<RecentApplication | null>(null);
  const [tickets, setTickets] = useState<GrievanceTicket[]>(mockGrievanceTickets);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Approval modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalDraft, setModalDraft] = useState<GrievanceDraft | null>(null);
  const [modalResult, setModalResult] = useState<GrievanceSubmitResult | null>(null);

  const handleFormSubmit = useCallback((draft: GrievanceDraft) => {
    setModalDraft(draft);
    setModalResult(null);
    setModalOpen(true);
  }, []);

  const handleConfirmSubmit = useCallback(async () => {
    if (!modalDraft || !selectedApp) return;
    setIsSubmitting(true);
    try {
      const result = await submitGrievance({
        applicationId: modalDraft.applicationId,
        applicationService: selectedApp.service,
        referenceNumber: selectedApp.referenceNumber || "",
        category: modalDraft.category as any,
        description: modalDraft.description,
        department: "Revenue Department",
        attachments: modalDraft.attachments.map((f, i) => ({
          id: `att_new_${i}`,
          name: f.name,
          size: f.size,
          type: f.type,
        })),
      });
      setModalResult(result);

      // Add the new ticket to the list
      const newTicket: GrievanceTicket = {
        id: result.ticketId,
        applicationId: modalDraft.applicationId,
        applicationService: selectedApp.service,
        referenceNumber: selectedApp.referenceNumber || "",
        category: modalDraft.category as any,
        description: modalDraft.description,
        department: "Revenue Department",
        status: "submitted",
        createdAt: result.submittedAt,
        updatedAt: result.submittedAt,
        attachments: modalDraft.attachments.map((f, i) => ({
          id: `att_new_${i}`,
          name: f.name,
          size: f.size,
          type: f.type,
        })),
      };
      setTickets((prev) => [newTicket, ...prev]);
    } finally {
      setIsSubmitting(false);
    }
  }, [modalDraft, selectedApp]);

  const openCount = tickets.filter(
    (t) => t.status === "submitted" || t.status === "under_review" || t.status === "in_progress"
  ).length;
  const resolvedCount = tickets.filter(
    (t) => t.status === "resolved" || t.status === "closed"
  ).length;

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
                <AlertCircle className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {openCount}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Active Grievances
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <Clock className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {tickets.filter((t) => t.status === "in_progress").length}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  In Progress
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {resolvedCount}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Resolved
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main two-column layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left — Application Selector */}
        <div className="lg:col-span-4">
          <Card className="sticky top-24">
            <CardHeader>
              <CardTitle className="text-base">Select Application</CardTitle>
            </CardHeader>
            <CardContent>
              <ApplicationSelector
                applications={mockRecentApplications}
                selectedId={selectedApp?.id ?? null}
                onSelect={setSelectedApp}
              />
            </CardContent>
          </Card>
        </div>

        {/* Right — Complaint Form */}
        <div className="lg:col-span-8">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">File a Grievance</CardTitle>
                {selectedApp && (
                  <Badge variant="info" className="text-xs">
                    {selectedApp.service}
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {!selectedApp ? (
                <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 py-12 text-center dark:border-slate-700">
                  <FileText className="h-10 w-10 text-slate-300 dark:text-slate-600" />
                  <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                    Select an application from the left panel to file a
                    grievance.
                  </p>
                </div>
              ) : (
                <ComplaintForm
                  selectedApplication={selectedApp}
                  onSubmit={handleFormSubmit}
                  isSubmitting={isSubmitting}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Submitted Grievances */}
      <div>
        <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">
          Submitted Grievances
        </h2>
        <SubmittedGrievances tickets={tickets} />
      </div>

      {/* Approval Modal */}
      <GrievanceApprovalModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        application={selectedApp}
        category={modalDraft?.category ?? ""}
        description={modalDraft?.description ?? ""}
        attachmentCount={modalDraft?.attachments.length ?? 0}
        onConfirm={handleConfirmSubmit}
        isSubmitting={isSubmitting}
        result={modalResult}
      />
    </div>
  );
}
