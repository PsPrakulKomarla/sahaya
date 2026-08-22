import { render, screen } from "@testing-library/react";
import { QuickActions } from "./QuickActions";

describe("QuickActions", () => {
  it("renders all four actions", () => {
    render(<QuickActions />);
    [
      "Apply Service",
      "Update Record",
      "Track Application",
      "Raise Grievance",
    ].forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  it("points each action to the correct route", () => {
    render(<QuickActions />);
    expect(
      screen.getByRole("link", { name: /apply service/i })
    ).toHaveAttribute("href", "/apply");
            expect(
      screen.getByRole("link", { name: /update record/i })
    ).toHaveAttribute("href", "/update");
    expect(
      screen.getByRole("link", { name: /track application/i })
    ).toHaveAttribute("href", "/applications");
    expect(
      screen.getByRole("link", { name: /raise grievance/i })
    ).toHaveAttribute("href", "/grievance");
  });

  it("renders an icon for every action", () => {
    render(<QuickActions />);
    expect(screen.getAllByRole("link")).toHaveLength(4);
  });
});
