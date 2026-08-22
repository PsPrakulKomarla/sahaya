import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { AIPromptBox } from "./AIPromptBox";

describe("AIPromptBox", () => {
  it("renders a large centered prompt with the required placeholder", () => {
    render(<AIPromptBox />);
    expect(
      screen.getByPlaceholderText("Example: Apply for an Income Certificate")
    ).toBeInTheDocument();
  });

  it("renders the four intent chips below the prompt", () => {
    render(<AIPromptBox />);
    expect(screen.getByRole("button", { name: "Apply" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Update" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Track" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Complaint" })).toBeInTheDocument();
  });

  it("renders the UI-only voice button", () => {
    render(<AIPromptBox />);
    expect(screen.getByRole("button", { name: "Use voice input" })).toBeInTheDocument();
  });

  it("disables the submit button when the prompt is empty", () => {
    render(<AIPromptBox />);
    expect(
      screen.getByRole("button", { name: /send to govflow ai/i })
    ).toBeDisabled();
  });

  it("submits via the placeholder agent hook and clears the input", async () => {
    render(<AIPromptBox />);
    const textarea = screen.getByPlaceholderText(
      "Example: Apply for an Income Certificate"
    ) as HTMLTextAreaElement;

    fireEvent.change(textarea, {
      target: { value: "Apply for an income certificate" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send to govflow ai/i }));

    // The hook is a placeholder: no fake AI response is rendered — the input
    // is simply consumed after the (no-op) submit resolves.
    await waitFor(() => {
      expect(textarea.value).toBe("");
    });
  });

  it("selecting an intent chip marks it as active", () => {
    render(<AIPromptBox />);
    const update = screen.getByRole("button", { name: "Update" });
    fireEvent.click(update);
    // Active chip uses the primary ring — assert it now carries the active style.
    expect(update).toHaveClass("ring-2");
  });
});
