import type {
  WizardConfig,
  ServiceOption,
  EligibilityCriteria,
  DocumentRequirement,
  FormSection,
} from "./types";

const applyServices: ServiceOption[] = [
  {
    id: "income_cert",
    name: "Income Certificate",
    department: "Revenue Department",
    description: "Apply for income certificate for various official purposes",
    estimatedTime: "3-5 days",
    category: "Revenue",
  },
  {
    id: "birth_cert",
    name: "Birth Certificate",
    department: "Civil Registration",
    description: "Register birth and obtain official birth certificate",
    estimatedTime: "7-10 days",
    category: "Civil Registration",
  },
  {
    id: "driving_license",
    name: "Driving License",
    department: "Transport Department",
    description: "Apply for new driving license or renewal",
    estimatedTime: "15-20 days",
    category: "Transport",
  },
  {
    id: "pension",
    name: "Pension Services",
    department: "Social Welfare",
    description: "Apply for government pension schemes",
    estimatedTime: "30-45 days",
    category: "Social Welfare",
  },
  {
    id: "property_tax",
    name: "Property Tax",
    department: "Municipal Corporation",
    description: "Pay property tax online",
    estimatedTime: "Instant",
    category: "Municipal",
  },
  {
    id: "caste_cert",
    name: "Caste Certificate",
    department: "Revenue Department",
    description: "Apply for caste certificate",
    estimatedTime: "7-15 days",
    category: "Revenue",
  },
];

const updateServices: ServiceOption[] = [
  {
    id: "aadhaar_update",
    name: "Aadhaar Update",
    department: "UIDAI",
    description: "Update name, address, mobile number, or other details",
    estimatedTime: "7-15 days",
    category: "Identity",
  },
  {
    id: "pan_update",
    name: "PAN Card Update",
    department: "Income Tax Department",
    description: "Update details in PAN card",
    estimatedTime: "15-20 days",
    category: "Finance",
  },
  {
    id: "voter_update",
    name: "Voter ID Update",
    department: "Election Commission",
    description: "Update voter registration details",
    estimatedTime: "15-30 days",
    category: "Electoral",
  },
  {
    id: "ration_update",
    name: "Ration Card Update",
    department: "Food & Civil Supplies",
    description: "Add/remove family members in ration card",
    estimatedTime: "7-15 days",
    category: "Social Welfare",
  },
];

const defaultEligibility: EligibilityCriteria[] = [
  {
    id: "age",
    label: "Age Requirement",
    description: "Applicant must be 18 years or older",
    met: true,
    required: true,
  },
  {
    id: "residence",
    label: "Residency Proof",
    description: "Must be a resident of the state",
    met: true,
    required: true,
  },
  {
    id: "aadhaar",
    label: "Valid Aadhaar",
    description: "Must have a valid Aadhaar card linked to mobile",
    met: true,
    required: true,
  },
  {
    id: "income_limit",
    label: "Income Limit",
    description: "Annual household income must be below the threshold",
    met: true,
    required: false,
  },
  {
    id: "category",
    label: "Category Certificate",
    description: "If applicable, provide category certificate",
    met: false,
    required: false,
  },
];

const defaultDocuments: DocumentRequirement[] = [
  {
    id: "aadhaar",
    name: "Aadhaar Card",
    description: "Front and back copy of Aadhaar card",
    status: "verified",
    uploadedAt: "2024-03-15",
  },
  {
    id: "address_proof",
    name: "Address Proof",
    description: "Utility bill, voter ID, or passport as address proof",
    status: "uploaded",
    uploadedAt: "2024-03-15",
  },
  {
    id: "photo",
    name: "Passport Photo",
    description: "Recent passport-size photograph (JPEG/PNG)",
    status: "uploaded",
    uploadedAt: "2024-03-15",
  },
  {
    id: "income_proof",
    name: "Income Proof",
    description: "Salary slips, Form 16, or income declaration",
    status: "required",
  },
  {
    id: "bank_statement",
    name: "Bank Statement",
    description: "Last 6 months bank statement",
    status: "missing",
  },
];

const defaultFormSections: FormSection[] = [
  {
    id: "personal",
    title: "Personal Information",
    description: "Basic details about the applicant",
    fields: [
      {
        id: "full_name",
        label: "Full Name",
        type: "text",
        placeholder: "Enter your full name as per Aadhaar",
        required: true,
        value: "Rajesh Kumar",
      },
      {
        id: "date_of_birth",
        label: "Date of Birth",
        type: "date",
        required: true,
        value: "1990-05-15",
      },
      {
        id: "gender",
        label: "Gender",
        type: "select",
        required: true,
        value: "male",
        options: [
          { label: "Male", value: "male" },
          { label: "Female", value: "female" },
          { label: "Other", value: "other" },
        ],
      },
      {
        id: "phone",
        label: "Mobile Number",
        type: "phone",
        placeholder: "10-digit mobile number",
        required: true,
        value: "9876543210",
      },
      {
        id: "email",
        label: "Email Address",
        type: "email",
        placeholder: "your@email.com",
        required: false,
      },
    ],
  },
  {
    id: "address",
    title: "Address Details",
    description: "Current residential address",
    fields: [
      {
        id: "house_number",
        label: "House/Flat Number",
        type: "text",
        placeholder: "e.g., 42-A",
        required: true,
      },
      {
        id: "street",
        label: "Street/Locality",
        type: "text",
        placeholder: "Street name or locality",
        required: true,
      },
      {
        id: "city",
        label: "City/Town",
        type: "text",
        placeholder: "City or town name",
        required: true,
      },
      {
        id: "pincode",
        label: "PIN Code",
        type: "text",
        placeholder: "6-digit PIN code",
        required: true,
        validation: {
          pattern: "^[0-9]{6}$",
          message: "Must be a valid 6-digit PIN code",
        },
      },
      {
        id: "state",
        label: "State",
        type: "select",
        required: true,
        value: "karnataka",
        options: [
          { label: "Karnataka", value: "karnataka" },
          { label: "Maharashtra", value: "maharashtra" },
          { label: "Tamil Nadu", value: "tamil_nadu" },
          { label: "Kerala", value: "kerala" },
          { label: "Andhra Pradesh", value: "andhra_pradesh" },
        ],
      },
    ],
  },
  {
    id: "service_specific",
    title: "Service Details",
    description: "Additional information for this service",
    fields: [
      {
        id: "purpose",
        label: "Purpose of Application",
        type: "select",
        required: true,
        options: [
          { label: "Education", value: "education" },
          { label: "Employment", value: "employment" },
          { label: "Legal", value: "legal" },
          { label: "Government Scheme", value: "scheme" },
          { label: "Other", value: "other" },
        ],
      },
      {
        id: "remarks",
        label: "Additional Remarks",
        type: "textarea",
        placeholder: "Any additional information you want to provide",
        required: false,
      },
    ],
  },
];

export const applyWorkflowConfig: WizardConfig = {
  mode: "apply",
  services: applyServices,
  eligibility: defaultEligibility,
  documents: defaultDocuments,
  formSections: defaultFormSections,
};

export const updateWorkflowConfig: WizardConfig = {
  mode: "update",
  services: updateServices,
  eligibility: defaultEligibility,
  documents: defaultDocuments,
  formSections: defaultFormSections,
};
