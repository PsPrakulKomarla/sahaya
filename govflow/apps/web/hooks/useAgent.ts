/**
 * Placeholder agent hook.
 *
 * IMPORTANT: This is intentionally a stub. It does NOT call any AI model and
 * does NOT generate fake AI responses. It only records the submitted request
 * and exposes loading/error state so the dashboard UI can be wired up later.
 */
import { useCallback, useState } from "react";
import type { AgentRequest, AgentResponse } from "@/lib/api/types";

export interface UseAgentResult {
  submit: (request: AgentRequest) => Promise<AgentResponse>;
  isLoading: boolean;
  error: string | null;
  lastRequest: AgentRequest | null;
}

export function useAgent(): UseAgentResult {
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRequest, setLastRequest] = useState<AgentRequest | null>(null);

  const submit = useCallback(
    (request: AgentRequest) => {
      let cancelled = false;
      setLoading(true);
      setError(null);
      setLastRequest(request);
      return new Promise<AgentResponse>((resolve) => {
        // Simulate minimal async handling. No AI response text is produced.
        setTimeout(() => {
          if (cancelled) return;
          setLoading(false);
          resolve({
            ok: true,
            intent: request.intent,
            input: request.input,
          });
        }, 400);
      });
    },
    [setLoading, setError, setLastRequest]
  );

  // A real implementation would also expose an `abort` to cancel the request;
  // omitted here because the hook is a placeholder.
  return { submit, isLoading, error, lastRequest };
}