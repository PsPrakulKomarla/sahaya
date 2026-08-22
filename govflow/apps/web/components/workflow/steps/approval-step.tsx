"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle,
  Clock,
  FileText,
  Download,
  MessageSquare,
  ArrowRight,
  Copy,
} from "lucide-react";

interface ApprovalStepProps {
  referenceNumber?: string;
  serviceName?: string;
  estimatedTime?: string;
  className?: string;
}

export function ApprovalStep({
  referenceNumber = "GOV/2024/001234",
  serviceName = "Income Certificate",
  estimatedTime = "3-5 working days",
  className,
}: ApprovalStepProps) {
  return (
    <div className={cn("p-4 sm:p-6 space-y-6", className)}>
      <div className="text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
          <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
        </div>
        <h2 className="mt-4 text-xl font-bold text-slate-900 dark:text-white">
          Application Submitted Successfully!
        </h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Your application for <strong>{serviceName}</strong> has been received
        </p>
      </div>

      <Card className="border-green-200 dark:border-green-900">
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">
              Reference Number
            </span>
            <div className="flex items-center gap-2">
              <Badge variant="success" className="font-mono text-sm">
                {referenceNumber}
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => navigator.clipboard.writeText(referenceNumber)}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="h-px bg-slate-200 dark:bg-slate-800" />
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">
              Service
            </span>
            <span className="text-sm font-medium text-slate-900 dark:text-white">
              {serviceName}
            </span>
          </div>
          <div className="h-px bg-slate-200 dark:bg-slate-800" />
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">
              Estimated Processing Time
            </span>
            <div className="flex items-center gap-1 text-sm font-medium text-slate-900 dark:text-white">
              <Clock className="h-4 w-4 text-gov-blue" />
              {estimatedTime}
            </div>
          </div>
          <div className="h-px bg-slate-200 dark:bg-slate-800" />
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500 dark:text-slate-400">
              Status
            </span>
            <Badge variant="warning">
              <span className="mr-1 h-1.5 w-1.5 rounded-full bg-yellow-500 animate-pulse" />
              Under Review
            </Badge>
          </div>
        </CardContent>
      </Card>

      <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
        <p className="text-sm text-blue-800 dark:text-blue-300">
          <strong>What happens next?</strong>
        </p>
        <ul className="mt-2 space-y-2 text-sm text-blue-700 dark:text-blue-400">
          <li className="flex items-start gap-2">
            <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-blue-500 shrink-0" />
            Your application will be reviewed by the department
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-blue-500 shrink-0" />
            You will receive SMS/email updates on your registered contacts
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-blue-500 shrink-0" />
            Track status anytime using your reference number
          </li>
        </ul>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Button variant="outline" className="flex-1">
          <Download className="mr-2 h-4 w-4" />
          Download Receipt
        </Button>
        <Button variant="outline" className="flex-1">
          <MessageSquare className="mr-2 h-4 w-4" />
          Contact Support
        </Button>
        <Button className="flex-1">
          Track Application
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
