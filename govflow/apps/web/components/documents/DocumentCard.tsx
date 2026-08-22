"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn, formatDate } from "@/lib/utils";
import type { VaultDocument, DocumentStatus } from "@/lib/api/types";
import {
  FileText,
  Image,
  Eye,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  ShieldCheck,
} from "lucide-react";

interface DocumentCardProps {
  document: VaultDocument;
  onPreview: (doc: VaultDocument) => void;
  onDelete: (docId: string) => void;
}

const STATUS_CONFIG: Record<
  DocumentStatus,
  { label: string; variant: "success" | "warning" | "destructive" | "info"; icon: React.ElementType }
> = {
  verified: {
    label: "Verified",
    variant: "success",
    icon: CheckCircle2,
  },
  processing: {
    label: "Processing",
    variant: "info",
    icon: Loader2,
  },
  needs_review: {
    label: "Needs Review",
    variant: "warning",
    icon: AlertTriangle,
  },
  rejected: {
    label: "Rejected",
    variant: "destructive",
    icon: XCircle,
  },
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const FILE_ICONS: Record<string, React.ElementType> = {
  pdf: FileText,
  png: Image,
  jpg: Image,
  jpeg: Image,
};

export function DocumentCard({ document, onPreview, onDelete }: DocumentCardProps) {
  const status = STATUS_CONFIG[document.status];
  const StatusIcon = status.icon;
  const FileIcon = FILE_ICONS[document.type] || FileText;

  return (
    <div className="group flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
      {/* File icon */}
      <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800">
        <FileIcon className="h-6 w-6 text-slate-500 dark:text-slate-400" />
      </div>

      {/* Info */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
            {document.name}
          </p>
          {document.status === "verified" && (
            <ShieldCheck className="h-4 w-4 flex-shrink-0 text-green-500" aria-label="Verified document" />
          )}
        </div>
        <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
          {document.category} &middot; {formatFileSize(document.size)} &middot;{" "}
          {formatDate(document.uploadedAt)}
        </p>
      </div>

      {/* Status badge */}
      <Badge variant={status.variant} className="flex-shrink-0 gap-1">
        <StatusIcon
          className={cn(
            "h-3 w-3",
            document.status === "processing" && "animate-spin"
          )}
        />
        {status.label}
      </Badge>

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Preview ${document.name}`}
          onClick={() => onPreview(document)}
        >
          <Eye className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Delete ${document.name}`}
          onClick={() => onDelete(document.id)}
        >
          <Trash2 className="h-4 w-4 text-red-500" />
        </Button>
      </div>
    </div>
  );
}
