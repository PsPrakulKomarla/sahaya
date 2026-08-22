import { render, screen } from "@testing-library/react";
import { GovernmentTips } from "./GovernmentTips";

describe("GovernmentTips", () => {
  it("renders the section heading", () => {
    render(<GovernmentTips />);
    expect(
      screen.getByText("Tips for a smooth application")
    ).toBeInTheDocument();
  });

  it("renders every government tip", () => {
    render(<GovernmentTips />);
    [
      "Gather documents first",
      "Keep reference numbers safe",
      "Verify official portals",
      "Apply during business hours",
    ].forEach((title) => {
      expect(screen.getByText(title)).toBeInTheDocument();
    });
  });
});
