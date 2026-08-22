"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type {
  RecentApplication,
  GrievanceCategory,
  GrievanceDraft,
} from "@/lib/api/types";
import { GRIEVANCE_CATEGORY_LABELS } from "@/lib/api/types";
import {
  FileText,
  Upload,
  X,
  Sparkles,
  Send,
  Loader2,
  AlertCircle,
} from "lucide-react";

interface ComplaintFormProps {
  selectedApplication: RecentApplication | null;
  onSubmit: (draft: GrievanceDraft) => void;
  isSubmitting: boolean;
}

const CATEGORIES: GrievanceCategory[] = [
  "delay",
  "incorrect_info",
  "missing_update",
  "technical_issue",
  "other",
];

const CATEGORY_ICONS: Record<GrievanceCategory, React.ElementType> = {
  delay: FileText,
  incorrect_info: AlertCircle,
  missing_update: FileText,
  technical_issue: AlertCircle,
  other: FileText,
};

export function ComplaintForm({
  selectedApplication,
  onSubmit,
  isSubmitting,
}: ComplaintFormProps) {
  const [category, setCategory] = useState<GrievanceCategory | "">("");
  const [description, setDescription] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [showAiPreview, setShowAiPreview] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.files) return;
      setAttachments((prev) => [...prev, ...Array.from(e.target.files!)]);
      e.target.value = "";
    },
    []
  );

  const removeAttachment = useCallback((index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = useCallback(() => {
    if (!selectedApplication || !category || !description.trim()) return;
    onSubmit({
      applicationId: selectedApplication.id,
      category,
      description: description.trim(),
      attachments,
    });
  }, [selectedApplication, category, description, attachments, onSubmit]);

  const canSubmit =
    selectedApplication && category && description.trim().length >= 10;

  // AI-generated preview text based on inputs
  const aiPreviewText = selectedApplication
    ? `Dear Sir/Madam,\n\nI am writing to file a grievance regarding my ${selectedApplication.service} application (Ref: ${selectedApplication.referenceNumber}).\n\nIssue Category: ${category ? GRIEVANCE_CATEGORY_LABELS[category as GrievanceCategory] : "Not selected"}\n\n${description}\n\nI request you to kindly look into this matter and take necessary action at the earliest.\n\nThank you,\nRajesh Kumar`
    : "";

  return (
    <div className="space-y-5">
      {/* Reference auto-fill */}
      {selectedApplication && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-900">
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Filing grievance for
          </p>
          <p className="text-sm font-medium text-slate-900 dark:text-white">
            {selectedApplication.service}
          </p>
          <p className="font-mono text-xs text-slate-500 dark:text-slate-400">
            Ref: {selectedApplication.referenceNumber}
          </p>
        </div>
      )}

      {/* Category */}
      <div className="space-y-2">
        <label className="label">Issue Category *</label>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {CATEGORIES.map((cat) => {
            const Icon = CATEGORY_ICONS[cat];
            const isSelected = category === cat;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => setCategory(cat)}
                className={cn(
                  "flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-all",
                  isSelected
                    ? "border-gov-blue bg-blue-50 font-medium text-gov-blue dark:border-gov-blue-light dark:bg-blue-950/20"
                    : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-slate-700"
                )}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                {GRIEVANCE_CATEGORY_LABELS[cat]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label htmlFor="grievance-desc" className="label">
          Description *
        </label>
        <textarea
          id="grievance-desc"
          rows={5}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe your issue in detail. Include dates, reference numbers, and any relevant information..."
          className={cn(
            "input min-h-[120px] resize-y"
          )}
        />
        <p className="text-xs text-slate-400 dark:text-slate-500">
          {description.length}/500 characters &middot; Minimum 10 characters
        </p>
      </div>

      {/* Attachment upload */}
      <div className="space-y-2">
        <label className="label">Attachments</label>
        <div
          onClick={() => fileInputRef.current?.click()}
          className="flex cursor-pointer items-center gap-2 rounded-lg border border-dashed border-slate-300 px-4 py-3 text-sm text-slate-500 transition-colors hover:border-gov-blue hover:text-gov-blue dark:border-slate-700 dark:text-slate-400 dark:hover:border-gov-blue-light"
        >
          <Upload className="h-4 w-4" />
          <span>Click to upload PDF, PNG, or JPG</span>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
          className="hidden"
          aria-hidden="true"
        />

        {attachments.length > 0 && (
          <div className="space-y-1.5">
            {attachments.map((file, i) => (
              <div
                key={`${file.name}-${i}`}
                className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 dark:border-slate-800 dark:bg-slate-900"
              >
                <FileText className="h-4 w-4 flex-shrink-0 text-slate-400" />
                <span className="min-w-0 flex-1 truncate text-xs text-slate-700 dark:text-slate-300">
                  {file.name}
                </span>
                <span className="text-[10px] text-slate-400">
                  {(file.size / 1024).toFixed(0)} KB
                </span>
                <button
                  type="button"
                  onClick={() => removeAttachment(i)}
                  className="flex-shrink-0 rounded p-0.5 text-slate-400 hover:text-red-500"
                  aria-label={`Remove ${file.name}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Complaint Preview */}
      <div className="space-y-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setShowAiPreview(!showAiPreview)}
          disabled={!selectedApplication || !category || !description}
          className="gap-1.5"
        >
          <Sparkles className="h-3.5 w-3.5 text-amber-500" />
          {showAiPreview ? "Hide" : "Show"} AI Complaint Preview
        </Button>

        {showAiPreview && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 dark:border-amber-900/30 dark:bg-amber-950/10">
            <div className="mb-2 flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-amber-500" />
              <span className="text-xs font-medium text-amber-700 dark:text-amber-400">
                AI-Generated Complaint Draft
              </span>
            </div>
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-700 dark:text-slate-300">
              {aiPreviewText}
            </pre>
          </div>
        )}
      </div>

      {/* Submit */}
      <Button
        onClick={handleSubmit}
        disabled={!canSubmit || isSubmitting}
        className="w-full gap-2"
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
            Submit Grievance
          </>
        )}
      </Button>
    </div>
  );
}
