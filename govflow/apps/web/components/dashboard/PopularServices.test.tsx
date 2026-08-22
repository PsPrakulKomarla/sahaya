import { render, screen } from "@testing-library/react";
import { PopularServices } from "./PopularServices";

describe("PopularServices", () => {
  it("renders every popular service", () => {
    render(<PopularServices />);
    [
      "Income Certificate",
      "Driving License",
      "Birth Certificate",
      "Aadhaar Update",
      "Senior Citizen Pension",
      "Property Tax Payment",
    ].forEach((name) => {
      expect(screen.getByText(name)).toBeInTheDocument();
    });
  });

  it("renders a link for each service", () => {
    render(<PopularServices />);
    expect(screen.getAllByRole("link")).toHaveLength(6);
  });
});
