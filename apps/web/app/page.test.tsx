import { render, screen } from "@testing-library/react";
import HomePage from "./page";

describe("HomePage", () => {
  it("renders the main heading", () => {
    render(<HomePage />);
    expect(screen.getByText("Government Services, Simplified")).toBeInTheDocument();
  });

  it("renders the Get Started button", () => {
    render(<HomePage />);
    expect(screen.getByRole("link", { name: /get started/i })).toBeInTheDocument();
  });

  it("renders supported services", () => {
    render(<HomePage />);
    expect(screen.getByText("Income Certificate")).toBeInTheDocument();
    expect(screen.getByText("Driving License")).toBeInTheDocument();
  });
});