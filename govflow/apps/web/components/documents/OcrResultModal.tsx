"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { VaultDocument, OcrData } from "@/lib/api/types";
import { ScanText, Check, X } from "lucide-react";

interface OcrResultModalProps {
  document: VaultDocument | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (docId: string, data: OcrData) => void;
}

export function OcrResultModal({
  document,
  open,
  onOpenChange,
  onConfirm,
}: OcrResultModalProps) {
  const [formData, setFormData] = useState<OcrData>({
    name: "",
    dateOfBirth: "",
    address: "",
    documentType: "",
  });

  useEffect(() => {
    if (open && document?.extractedData) {
      setFormData({ ...document.extractedData });
    } else if (open && document) {
      setFormData({
        name: "",
        dateOfBirth: "",
        address: "",
        documentType: document.category,
      });
    }
  }, [open, document]);

  const handleFieldChange = (field: keyof OcrData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleConfirm = () => {
    if (!document) return;
    onConfirm(document.id, formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ScanText className="h-5 w-5 text-gov-blue" />
            OCR Extracted Data
          </DialogTitle>
          <DialogDescription>
            {document
              ? `Review the extracted data from "${document.name}". Edit fields if needed before confirming.`
              : "Review and confirm the extracted data."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <label htmlFor="ocr-name" className="label">
              Full Name
            </label>
            <Input
              id="ocr-name"
              value={formData.name}
              onChange={(e) => handleFieldChange("name", e.target.value)}
              placeholder="Enter full name"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="ocr-dob" className="label">
              Date of Birth
            </label>
            <Input
              id="ocr-dob"
              type="date"
              value={formData.dateOfBirth}
              onChange={(e) =>
                handleFieldChange("dateOfBirth", e.target.value)
              }
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="ocr-address" className="label">
              Address
            </label>
            <Input
              id="ocr-address"
              value={formData.address}
              onChange={(e) => handleFieldChange("address", e.target.value)}
              placeholder="Enter address"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="ocr-doc-type" className="label">
              Document Type
            </label>
            <Input
              id="ocr-doc-type"
              value={formData.documentType}
              onChange={(e) =>
                handleFieldChange("documentType", e.target.value)
              }
              placeholder="e.g. Aadhaar Card, PAN Card"
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="gap-1"
          >
            <X className="h-4 w-4" />
            Cancel
          </Button>
          <Button onClick={handleConfirm} className="gap-1">
            <Check className="h-4 w-4" />
            Confirm & Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
