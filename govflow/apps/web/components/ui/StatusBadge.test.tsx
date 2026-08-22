import { render, screen } from "@testing-library/react";
import type { ApplicationStatus } from "@govflow/shared";
import { StatusBadge } from "./StatusBadge";

describe("StatusBadge", () => {
  const cases: Array<[ApplicationStatus, string]> = [
    ["approved", "Approved"],
    ["under_review", "Under Review"],
    ["rejected", "Rejected"],
    ["pending_action", "Action Required"],
    ["submitted", "Submitted"],
    ["draft", "Draft"],
    ["expired", "Expired"],
  ];

  it.each(cases)("renders the label for %s", (status, label) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });
});
