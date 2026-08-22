"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { useAgent } from "@/hooks/useAgent";
import { VoiceButton } from "@/components/dashboard/VoiceButton";
import { PROMPT_INTENT_OPTIONS } from "@/lib/mock-data";
import type { IntentType } from "@govflow/shared";
import { cn } from "@/lib/utils";

/**
 * Large, centered AI prompt control for the citizen dashboard.
 *
 * It only calls the placeholder `useAgent` hook on submit — it never renders a
 * fake AI response. Intent chips let the citizen scope the request (Apply,
 * Update, Track, Complaint).
 */
export function AIPromptBox() {
  const [input, setInput] = useState("");
  const [intent, setIntent] = useState<IntentType>("NEW_APPLICATION");
  const { submit, isLoading, error } = useAgent();

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    await submit({ input: input.trim(), intent });
    // Consume the prompt. No AI reply is generated at this phase.
    setInput("");
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <section className="w-full max-w-2xl mx-auto">
      <div className="card">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Example: Apply for an Income Certificate"
            className="input min-h-[100px] resize-none pr-12 text-base leading-relaxed"
            rows={3}
            disabled={isLoading}
            aria-label="What government service do you need?"
          />
          <VoiceButton className="pointer-events-none" />
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {PROMPT_INTENT_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setIntent(option.value)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                intent === option.value
                  ? "bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300 ring-2 ring-primary-500"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              )}
            >
              {option.label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className="btn-primary w-full mt-4 text-base"
        >
          <Send className="h-4 w-4 mr-2" />
          {isLoading ? "Sending…" : "Send to GovFlow AI"}
        </button>

        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

        <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
          This is a placeholder. The AI agent will be enabled in a later phase —
          no response is generated yet.
        </p>
      </div>
    </section>
  );
}