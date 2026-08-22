export interface ServiceCapability {
  value: string;
  label: string;
}

export const SERVICE_CAPABILITIES: ServiceCapability[] = [
  { value: "discover", label: "Discover" },
  { value: "eligibility_check", label: "Check Eligibility" },
  { value: "document_requirements", label: "Document Requirements" },
  { value: "new_application", label: "Apply" },
  { value: "update_record", label: "Update Record" },
  { value: "renew", label: "Renew" },
  { value: "track_application", label: "Track Application" },
  { value: "raise_grievance", label: "Raise Grievance" },
];

export function getCapabilityLabel(capability: string): string {
  const found = SERVICE_CAPABILITIES.find((c) => c.value === capability);
  return found?.label ?? capability;
}

export function getCapabilityIcon(capability: string): string {
  const icons: Record<string, string> = {
    discover: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
    eligibility_check: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    document_requirements: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
    new_application: "M12 4v16m8-8H4",
    update_record: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
    renew: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15",
    track_application: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2",
    raise_grievance: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
  };
  return icons[capability] || "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z";
}