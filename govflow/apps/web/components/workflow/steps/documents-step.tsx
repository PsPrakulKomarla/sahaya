"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  CheckCircle,
  Upload,
  FileText,
  Clock,
  AlertCircle,
  Eye,
  Trash2,
  Info,
} from "lucide-react";
import type { DocumentRequirement } from "../types";

interface DocumentChecklistItemProps {
  document: DocumentRequirement;
  onUpload?: (documentId: string) => void;
  onRemove?: (documentId: string) => void;
  className?: string;
}

export function DocumentChecklistItem({
  document: doc,
  onUpload,
  onRemove,
  className,
}: DocumentChecklistItemProps) {
  const statusConfig = {
    required: {
      label: "Required",
      color: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
      icon: FileText,
      badge: "outline" as const,
    },
    uploaded: {
      label: "Uploaded",
      color: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
      icon: Upload,
      badge: "info" as const,
    },
    missing: {
      label: "Missing",
      color: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
      icon: AlertCircle,
      badge: "destructive" as const,
    },
    verified: {
      label: "Verified",
      color: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
      icon: CheckCircle,
      badge: "success" as const,
    },
  };

  const config = statusConfig[doc.status];
  const StatusIcon = config.icon;

  return (
    <Card className={cn("transition-all", className)}>
      <CardContent className="p-4">
        <div className="flex items-center gap-4">
          <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg shrink-0", config.color)}>
            <StatusIcon className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                {doc.name}
              </p>
              <Badge variant={config.badge} className="text-[10px] shrink-0">
                {config.label}
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
              {doc.description}
            </p>
            {doc.uploadedAt && (
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Uploaded {doc.uploadedAt}
              </p>
            )}
            {doc.verificationNote && (
              <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                {doc.verificationNote}
              </p>
            )}
          </div>
          <div className="flex items-center gap-1 shrink-0">
            {doc.status === "required" || doc.status === "missing" ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onUpload?.(doc.id)}
              >
                <Upload className="mr-1 h-3 w-3" />
                Upload
              </Button>
            ) : (
              <>
                <Button size="icon" variant="ghost" className="h-8 w-8">
                  <Eye className="h-4 w-4" />
                </Button>
                {doc.status === "uploaded" && onRemove && (
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-8 w-8"
                    onClick={() => onRemove(doc.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                )}
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface DocumentChecklistProps {
  documents: DocumentRequirement[];
  onUpload?: (documentId: string) => void;
  onRemove?: (documentId: string) => void;
  className?: string;
}

export function DocumentChecklist({
  documents,
  onUpload,
  onRemove,
  className,
}: DocumentChecklistProps) {
  const verified = documents.filter((d) => d.status === "verified").length;
  const uploaded = documents.filter((d) => d.status === "uploaded").length;
  const required = documents.filter((d) => d.status === "required").length;
  const missing = documents.filter((d) => d.status === "missing").length;
  const total = documents.length;
  const progress = ((verified + uploaded) / total) * 100;

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-900 dark:text-white">
            Document Progress
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {verified + uploaded} of {total} documents ready
          </p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-slate-900 dark:text-white">
            {Math.round(progress)}%
          </p>
        </div>
      </div>
      <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className="h-2 rounded-full bg-gov-blue transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex items-center gap-4 text-xs">
        <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
          <CheckCircle className="h-3 w-3" />
          {verified} verified
        </div>
        <div className="flex items-center gap-1 text-blue-600 dark:text-blue-400">
          <Upload className="h-3 w-3" />
          {uploaded} uploaded
        </div>
        {required > 0 && (
          <div className="flex items-center gap-1 text-slate-500">
            <FileText className="h-3 w-3" />
            {required} required
          </div>
        )}
        {missing > 0 && (
          <div className="flex items-center gap-1 text-red-600 dark:text-red-400">
            <AlertCircle className="h-3 w-3" />
            {missing} missing
          </div>
        )}
      </div>
    </div>
  );
}

interface DocumentsStepProps {
  documents: DocumentRequirement[];
  onUpload?: (documentId: string) => void;
  onRemove?: (documentId: string) => void;
  className?: string;
}

export function DocumentsStep({
  documents,
  onUpload,
  onRemove,
  className,
}: DocumentsStepProps) {
  return (
    <div className={cn("p-4 sm:p-6 space-y-6", className)}>
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          Required Documents
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Upload the necessary documents for your application
        </p>
      </div>

      <DocumentChecklist
        documents={documents}
        onUpload={onUpload}
        onRemove={onRemove}
      />

      <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
        <div className="flex items-start gap-2">
          <Info className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800 dark:text-blue-300">
            <p className="font-medium">Document Tips</p>
            <ul className="mt-1 list-disc list-inside space-y-1 text-blue-700 dark:text-blue-400">
              <li>Upload clear, readable copies of documents</li>
              <li>Accepted formats: PDF, JPG, PNG (max 5MB each)</li>
              <li>Ensure all four corners of the document are visible</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {documents.map((doc) => (
          <DocumentChecklistItem
            key={doc.id}
            document={doc}
            onUpload={onUpload}
            onRemove={onRemove}
          />
        ))}
      </div>
    </div>
  );
}
