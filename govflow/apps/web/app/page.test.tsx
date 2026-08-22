import { render, screen } from "@testing-library/react";
import HomePage from "./page";

describe("HomePage (Citizen Dashboard)", () => {
  it("renders the dashboard hero title", () => {
    render(<HomePage />);
    expect(
      screen.getByRole("heading", {
        name: /tell govflow what government service you need/i,
      })
    ).toBeInTheDocument();
  });

  it("renders the hero subtitle", () => {
    render(<HomePage />);
    expect(
      screen.getByText(
        /apply, update, track or raise grievances using one ai agent/i
      )
    ).toBeInTheDocument();
  });

  it("renders the AI prompt box with the required placeholder", () => {
    render(<HomePage />);
    expect(
      screen.getByPlaceholderText("Example: Apply for an Income Certificate")
    ).toBeInTheDocument();
  });

  it("renders the four intent chips below the prompt", () => {
    render(<HomePage />);
    expect(screen.getByRole("button", { name: "Apply" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Update" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Track" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Complaint" })).toBeInTheDocument();
  });

  it("renders the UI-only voice button", () => {
    render(<HomePage />);
    expect(screen.getByLabelText("Use voice input")).toBeInTheDocument();
  });

  it("renders quick actions that navigate to the correct pages", () => {
    render(<HomePage />);
    expect(screen.getByRole("link", { name: /apply service/i })).toHaveAttribute(
      "href",
      "/apply"
    );
        expect(screen.getByRole("link", { name: /update record/i })).toHaveAttribute(
      "href",
      "/update"
    );
    expect(screen.getByRole("link", { name: /track application/i })).toHaveAttribute(
      "href",
      "/applications"
    );
    expect(screen.getByRole("link", { name: /raise grievance/i })).toHaveAttribute(
      "href",
      "/grievance"
    );
  });

  it("renders recent applications loaded from the mock API", async () => {
    render(<HomePage />);
    expect(screen.getByText("Recent Applications")).toBeInTheDocument();
    expect(
      await screen.findByText(/INC\/2024\/001847/)
    ).toBeInTheDocument();
    expect(screen.getByText("Under Review")).toBeInTheDocument();
  });

  it("renders popular services and government tips", () => {
    render(<HomePage />);
    expect(screen.getByText("Senior Citizen Pension")).toBeInTheDocument();
    expect(screen.getByText("Tips for a smooth application")).toBeInTheDocument();
  });
});
