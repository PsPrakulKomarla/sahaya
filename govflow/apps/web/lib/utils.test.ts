import { cn, formatDate } from "./utils";

describe("formatDate", () => {
  it("formats an ISO date string", () => {
    // en-IN locale: "DD Mon YYYY"
    expect(formatDate("2024-08-12T10:30:00Z")).toBe("12 Aug 2024");
  });

  it("throws on an invalid date", () => {
    expect(() => formatDate("not-a-date")).toThrow(RangeError);
  });
});

describe("cn", () => {
  it("merges conflicting tailwind classes", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });

  it("concatenates non-conflicting classes", () => {
    expect(cn("text-sm", "font-medium")).toBe("text-sm font-medium");
  });
});
