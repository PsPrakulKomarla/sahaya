import { Mic } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Voice input button.
 *
 * This component is UI only — it does not wire up speech recognition. The
 * microphone is rendered as a disabled affordance with a "coming soon"
 * tooltip so the control can be dropped into the prompt box without implying
 * working voice behaviour.
 */
export function VoiceButton({
  className,
  onClick,
  "aria-label": ariaLabel = "Use voice input",
}: {
  className?: string;
  onClick?: () => void;
  "aria-label"?: string;
}) {
  return (
    <button
      type="button"
      aria-label={ariaLabel}
      title="Voice input (coming soon)"
      onClick={onClick}
      disabled
      className={cn(
        "absolute right-2 top-2 inline-flex items-center justify-center rounded-lg p-2 text-slate-500 hover:text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:cursor-not-allowed",
        className
      )}
    >
      <Mic className="h-5 w-5" />
    </button>
  );
}