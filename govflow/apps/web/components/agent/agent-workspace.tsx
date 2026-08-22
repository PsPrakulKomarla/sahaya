"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ConversationPanel } from "./conversation/conversation-panel";
import { Timeline, type TimelineStep } from "./timeline";
import { BrowserPreview } from "./browser/browser-preview";
import {
  CurrentPortal,
  CurrentStep,
  ProgressCard,
  ConfidenceCard,
  RuntimeCard,
} from "./activity";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";
import { PanelRightOpen, PanelRightClose } from "lucide-react";

interface AgentWorkspaceProps {
  className?: string;
}

export function AgentWorkspace({ className }: AgentWorkspaceProps) {
  const [currentStep, setCurrentStep] = React.useState<TimelineStep>("reading_requirements");
  const [elapsed, setElapsed] = React.useState("02:34");
  const [activityOpen, setActivityOpen] = React.useState(true);

  // Mock runtime timer
  React.useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => {
        const [min, sec] = prev.split(":").map(Number);
        const totalSec = min * 60 + sec + 1;
        const newMin = Math.floor(totalSec / 60);
        const newSec = totalSec % 60;
        return `${String(newMin).padStart(2, "0")}:${String(newSec).padStart(2, "0")}`;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={cn("flex h-[calc(100vh-4rem)]", className)}>
      {/* Left Panel - Conversation */}
      <div className="flex-1 flex flex-col min-w-0 border-r border-slate-200 dark:border-slate-800">
        <ConversationPanel />
      </div>

      {/* Right Panel - Agent Activity (Desktop) */}
      <div
        className={cn(
          "hidden lg:flex flex-col transition-all duration-300",
          activityOpen ? "w-[420px]" : "w-0"
        )}
      >
        {activityOpen && (
          <div className="flex flex-col h-full overflow-hidden">
            {/* Activity Header */}
            <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-950">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                Agent Activity
              </h2>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => setActivityOpen(false)}
              >
                <PanelRightClose className="h-4 w-4" />
              </Button>
            </div>

            {/* Activity Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Activity Cards */}
              <CurrentPortal
                name="Karnataka Revenue Department"
                url="https://service.karnataka.gov.in"
                status="active"
              />

              <CurrentStep
                step="Filling Application Form"
                description="Auto-filling personal details from Aadhaar data"
                stepNumber={3}
                totalSteps={7}
              />

              <div className="grid grid-cols-2 gap-4">
                <ProgressCard
                  label="Form Progress"
                  value={45}
                  color="bg-gov-blue"
                />
                <ProgressCard
                  label="Document Verification"
                  value={80}
                  color="bg-green-500"
                />
              </div>

              <ConfidenceCard value={87} />

              <RuntimeCard elapsed={elapsed} isRunning={true} />

              {/* Timeline */}
              <Timeline currentStep={currentStep} />

              {/* Browser Preview */}
              <BrowserPreview
                url="https://service.karnataka.gov.in/income-cert"
                pageTitle="Income Certificate Application"
                isLoading={false}
              />
            </div>
          </div>
        )}
      </div>

      {/* Collapsed Toggle (Desktop) */}
      {!activityOpen && (
        <div className="hidden lg:flex items-start pt-4 pr-2">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => setActivityOpen(true)}
          >
            <PanelRightOpen className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Mobile Activity Panel */}
      <div className="lg:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="outline"
              size="icon"
              className="fixed bottom-24 right-4 z-40 h-12 w-12 rounded-full shadow-lg"
            >
              <PanelRightOpen className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-[90vw] sm:w-[400px] p-0">
            <SheetTitle className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
              Agent Activity
            </SheetTitle>
            <div className="overflow-y-auto h-[calc(100vh-3.5rem)] p-4 space-y-4">
              <CurrentPortal
                name="Karnataka Revenue Department"
                url="https://service.karnataka.gov.in"
                status="active"
              />

              <CurrentStep
                step="Filling Application Form"
                description="Auto-filling personal details from Aadhaar data"
                stepNumber={3}
                totalSteps={7}
              />

              <div className="grid grid-cols-2 gap-4">
                <ProgressCard
                  label="Form Progress"
                  value={45}
                  color="bg-gov-blue"
                />
                <ProgressCard
                  label="Document Verification"
                  value={80}
                  color="bg-green-500"
                />
              </div>

              <ConfidenceCard value={87} />

              <RuntimeCard elapsed={elapsed} isRunning={true} />

              <Timeline currentStep={currentStep} />

              <BrowserPreview
                url="https://service.karnataka.gov.in/income-cert"
                pageTitle="Income Certificate Application"
                isLoading={false}
              />
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </div>
  );
}
