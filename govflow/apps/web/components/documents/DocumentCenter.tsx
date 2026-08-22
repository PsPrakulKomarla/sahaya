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
import { UploadZone } from "./UploadZone";
import { DocumentCard } from "./DocumentCard";
import { OcrResultModal } from "./OcrResultModal";
import { mockDocuments, UPLOAD_CONFIG } from "@/lib/mock-data";
import type { VaultDocument, OcrData, DocumentStatus } from "@/lib/api/types";
import {
  FolderOpen,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  ShieldCheck,
  Trash2,
} from "lucide-react";

const STATUS_SUMMARY_CONFIG: Record<
  DocumentStatus,
  { label: string; color: string; icon: React.ElementType }
> = {
  verified: {
    label: "Verified",
    color:
      "bg-green-50 text-green-700 dark:bg-green-950/30 dark:text-green-400",
    icon: CheckCircle2,
  },
  processing: {
    label: "Processing",
    color: "bg-blue-50 text-blue-700 dark:bg-blue-950/30 dark:text-blue-400",
    icon: Loader2,
  },
  needs_review: {
    label: "Needs Review",
    color:
      "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400",
    icon: AlertTriangle,
  },
  rejected: {
    label: "Rejected",
    color: "bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-400",
    icon: XCircle,
  },
};

export function DocumentCenter() {
  const [documents, setDocuments] = useState<VaultDocument[]>(mockDocuments);
  const [previewDoc, setPreviewDoc] = useState<VaultDocument | null>(null);
  const [ocrModalDoc, setOcrModalDoc] = useState<VaultDocument | null>(null);
  const [ocrModalOpen, setOcrModalOpen] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // --- Upload handler ---
  const handleFilesAccepted = useCallback((files: File[]) => {
    const newDocs: VaultDocument[] = files.map((file, i) => ({
      id: `doc_new_${Date.now()}_${i}`,
      name: file.name,
      type: file.type.split("/")[1] as VaultDocument["type"],
      category: "Identity",
      size: file.size,
      status: "processing" as DocumentStatus,
      uploadedAt: new Date().toISOString(),
    }));
    setDocuments((prev) => [...newDocs, ...prev]);

    // Simulate OCR processing — after 2s the first processing doc becomes needs_review
    setTimeout(() => {
      setDocuments((prev) =>
        prev.map((d) =>
          d.status === "processing" && newDocs.some((n) => n.id === d.id)
            ? {
                ...d,
                status: "needs_review" as DocumentStatus,
                extractedData: {
                  name: "",
                  dateOfBirth: "",
                  address: "",
                  documentType: d.category,
                },
              }
            : d
        )
      );
    }, 2000);
  }, []);

  // --- Preview handler (opens OCR modal for docs with extracted data) ---
  const handlePreview = useCallback(
    (doc: VaultDocument) => {
      setPreviewDoc(doc);
      setOcrModalDoc(doc);
      setOcrModalOpen(true);
    },
    []
  );

  // --- OCR confirm handler ---
  const handleOcrConfirm = useCallback((docId: string, data: OcrData) => {
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === docId
          ? { ...d, extractedData: data, status: "verified" as DocumentStatus }
          : d
      )
    );
    setOcrModalOpen(false);
    setOcrModalDoc(null);
  }, []);

  // --- Delete handler ---
  const handleDelete = useCallback((docId: string) => {
    setDeleteConfirmId(docId);
  }, []);

  const confirmDelete = useCallback(() => {
    if (!deleteConfirmId) return;
    setDocuments((prev) => prev.filter((d) => d.id !== deleteConfirmId));
    setDeleteConfirmId(null);
  }, [deleteConfirmId]);

  // --- Stats ---
  const totalSize = documents.reduce((sum, d) => sum + d.size, 0);
  const maxStorage = 100 * 1024 * 1024; // 100 MB
  const storagePercent = Math.min((totalSize / maxStorage) * 100, 100);

  const statusCounts = documents.reduce(
    (acc, d) => {
      acc[d.status] = (acc[d.status] || 0) + 1;
      return acc;
    },
    {} as Record<DocumentStatus, number>
  );

  return (
    <div className="space-y-6">
      {/* Storage info */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FolderOpen className="h-5 w-5 text-gov-blue" />
              <div>
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  Storage Used
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {(totalSize / (1024 * 1024)).toFixed(1)} MB of{" "}
                  {maxStorage / (1024 * 1024)} MB &middot;{" "}
                  {documents.length} document{documents.length !== 1 && "s"}
                </p>
              </div>
            </div>
            <div className="h-2 w-32 rounded-full bg-slate-200 dark:bg-slate-800">
              <div
                className="h-2 rounded-full bg-gov-blue transition-all"
                style={{ width: `${storagePercent}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Verification status summary */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {(Object.entries(STATUS_SUMMARY_CONFIG) as [DocumentStatus, (typeof STATUS_SUMMARY_CONFIG)[DocumentStatus]][]).map(
          ([status, config]) => {
            const Icon = config.icon;
            const count = statusCounts[status] || 0;
            return (
              <div
                key={status}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 ${config.color}`}
              >
                <Icon
                  className={`h-4 w-4 ${
                    status === "processing" ? "animate-spin" : ""
                  }`}
                />
                <span className="text-xs font-medium">
                  {count} {config.label}
                </span>
              </div>
            );
          }
        )}
      </div>

      {/* Upload zone */}
      <div>
        <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">
          Upload Zone
        </h2>
        <UploadZone onFilesAccepted={handleFilesAccepted} />
      </div>

      {/* Uploaded documents */}
      <div>
        <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">
          Uploaded Documents
        </h2>
        {documents.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center dark:border-slate-700">
            <ShieldCheck className="mx-auto h-10 w-10 text-slate-300 dark:text-slate-600" />
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              No documents uploaded yet. Use the upload zone above to get
              started.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <DocumentCard
                key={doc.id}
                document={doc}
                onPreview={handlePreview}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>

      {/* Inline delete confirmation */}
      {deleteConfirmId && (
        <div className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-xl border border-slate-200 bg-white p-4 shadow-lg dark:border-slate-800 dark:bg-slate-900">
          <p className="text-sm text-slate-700 dark:text-slate-300">
            Are you sure you want to delete this document?
          </p>
          <div className="mt-3 flex justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDeleteConfirmId(null)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={confirmDelete}
              className="gap-1"
            >
              <Trash2 className="h-3 w-3" />
              Delete
            </Button>
          </div>
        </div>
      )}

      {/* OCR Result Modal */}
      <OcrResultModal
        document={ocrModalDoc}
        open={ocrModalOpen}
        onOpenChange={setOcrModalOpen}
        onConfirm={handleOcrConfirm}
      />
    </div>
  );
}
