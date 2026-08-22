import { act, renderHook } from "@testing-library/react";
import { useAgent } from "./useAgent";

describe("useAgent (placeholder)", () => {
  it("starts in an idle state with no request recorded", () => {
    const { result } = renderHook(() => useAgent());
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.lastRequest).toBeNull();
  });

  it("submits without generating AI content", async () => {
    const { result } = renderHook(() => useAgent());

    let response: Awaited<ReturnType<typeof result.current.submit>>;
    await act(async () => {
      response = await result.current.submit({
        input: "Apply for an income certificate",
        intent: "NEW_APPLICATION",
      });
    });

    // Placeholder behaviour: acknowledged but no AI content produced.
    expect(response!.ok).toBe(true);
    expect(response!.intent).toBe("NEW_APPLICATION");
    expect(response!.input).toBe("Apply for an income certificate");
    expect(response!.content).toBeUndefined();

    // The request is recorded; loading clears after the stub resolves.
    expect(result.current.lastRequest?.input).toBe("Apply for an income certificate");
    expect(result.current.isLoading).toBe(false);
  });
});
