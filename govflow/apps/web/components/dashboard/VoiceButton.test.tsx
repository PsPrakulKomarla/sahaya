import { render, screen } from "@testing-library/react";
import { VoiceButton } from "./VoiceButton";

describe("VoiceButton (UI only)", () => {
  it("renders with an accessible voice-label", () => {
    render(<VoiceButton />);
    expect(
      screen.getByRole("button", { name: "Use voice input" })
    ).toBeInTheDocument();
  });

  it("is a UI-only affordance (disabled, not wired to speech)", () => {
    render(<VoiceButton />);
    expect(
      screen.getByRole("button", { name: "Use voice input" })
    ).toBeDisabled();
  });

  it("uses a custom aria-label when provided", () => {
    render(<VoiceButton aria-label="Start voice recording" />);
    expect(
      screen.getByRole("button", { name: /start voice recording/i })
    ).toBeInTheDocument();
  });
});
