"use client";

import { useCallback, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { UPLOAD_CONFIG } from "@/lib/mock-data";
import { Upload, FileText, AlertCircle } from "lucide-react";

interface UploadZoneProps {
  onFilesAccepted: (files: File[]) => void;
}

export function UploadZone({ onFilesAccepted }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFiles = useCallback(
    (files: FileList | File[]): File[] => {
      const valid: File[] = [];
      setError(null);

      for (const file of Array.from(files)) {
        if (!UPLOAD_CONFIG.acceptedTypes.includes(file.type)) {
          setError(
            `"${file.name}" is not a supported format. Accepted: PDF, PNG, JPG, JPEG.`
          );
          continue;
        }
        if (file.size > UPLOAD_CONFIG.maxFileSizeMB * 1024 * 1024) {
          setError(
            `"${file.name}" exceeds the ${UPLOAD_CONFIG.maxFileSizeMB} MB limit.`
          );
          continue;
        }
        valid.push(file);
      }

      return valid;
    },
    []
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const valid = validateFiles(e.dataTransfer.files);
      if (valid.length > 0) onFilesAccepted(valid);
    },
    [onFilesAccepted, validateFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.files) return;
      const valid = validateFiles(e.target.files);
      if (valid.length > 0) onFilesAccepted(valid);
      e.target.value = "";
    },
    [onFilesAccepted, validateFiles]
  );

  return (
    <div className="space-y-2">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Upload documents by dragging files here or clicking to browse"
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        className={cn(
          "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 text-center transition-colors cursor-pointer",
          "bg-slate-50 dark:bg-slate-900/50",
          isDragging
            ? "border-gov-blue bg-blue-50 dark:bg-blue-950/20"
            : "border-slate-300 dark:border-slate-700 hover:border-gov-blue hover:bg-blue-50/50 dark:hover:bg-blue-950/10"
        )}
      >
        <div
          className={cn(
            "flex h-12 w-12 items-center justify-center rounded-full transition-colors",
            isDragging
              ? "bg-gov-blue text-white"
              : "bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400"
          )}
        >
          <Upload className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm font-medium text-slate-900 dark:text-white">
            {isDragging
              ? "Drop your files here"
              : "Drag & drop your documents here"}
          </p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            or click to browse
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500">
          <FileText className="h-3 w-3" />
          <span>
            PDF, PNG, JPG, JPEG &middot; Max {UPLOAD_CONFIG.maxFileSizeMB} MB
          </span>
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept={UPLOAD_CONFIG.acceptedTypes.join(",")}
        onChange={handleInputChange}
        className="hidden"
        aria-hidden="true"
      />

      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-950/30 dark:text-red-400">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
