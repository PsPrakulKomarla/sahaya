import { render, screen } from "@testing-library/react";
import {
  RecentApplications,
  RecentApplicationCard,
} from "./RecentApplications";
import type { RecentApplication } from "@/lib/api/types";
import { formatDate } from "@/lib/utils";

const sample: RecentApplication = {
  id: "app_01",
  serviceId: "svc_income",
  service: "Income Certificate",
  status: "under_review",
  date: "2024-08-12T10:30:00Z",
  referenceNumber: "INC/2024/001847",
  nextAction: "Upload remaining income proof",
};

describe("RecentApplicationCard (reusable card)", () => {
  it("renders service, status, date and reference number", () => {
    render(<RecentApplicationCard application={sample} />);

    expect(screen.getByText("Income Certificate")).toBeInTheDocument();
    // Status badge
    expect(screen.getByText("Under Review")).toBeInTheDocument();
    // Date is rendered via formatDate
    expect(screen.getByText(formatDate(sample.date))).toBeInTheDocument();
    // Reference number
    expect(screen.getByText(/INC\/2024\/001847/)).toBeInTheDocument();
    // Next-action hint
    expect(screen.getByText(/next: upload remaining income proof/i)).toBeInTheDocument();
  });

  it("opens the application on click", () => {
    render(<RecentApplicationCard application={sample} />);
    expect(screen.getByRole("link", { name: "Open" })).toHaveAttribute(
      "href",
      "/applications/app_01"
    );
  });

  it("renders without a reference number", () => {
    const noRef = { ...sample, referenceNumber: undefined };
    render(<RecentApplicationCard application={noRef} />);
    expect(screen.getByText("Reference: —")).toBeInTheDocument();
  });
});

describe("RecentApplications", () => {
  it("renders a heading and loads applications from the mock API", async () => {
    render(<RecentApplications />);
    expect(screen.getByText("Recent Applications")).toBeInTheDocument();
    expect(await screen.findByText("Income Certificate")).toBeInTheDocument();
    expect(screen.getAllByTestId("application-card")).toHaveLength(3);
  });

  it("renders a reference number for each loaded application", async () => {
    render(<RecentApplications />);
    expect(await screen.findByText(/INC\/2024\/001847/)).toBeInTheDocument();
    expect(screen.getByText(/DL\/REN\/2024\/033210/)).toBeInTheDocument();
    expect(screen.getByText(/CASTE\/2024\/009521/)).toBeInTheDocument();
  });
});
