type Database = {
  public: {
    Tables: {
      grievances: {
        Row: {
          id: string;
          application_id: string;
          reference_number: string;
          category: string;
          description: string;
          department: string;
          status: string;
          created_at: string;
          updated_at: string;
          attachments: any[];
        };
        Insert: {
          id: string;
          application_id: string;
          reference_number: string;
          category: string;
          description: string;
          department: string;
          status: string;
          created_at: string;
          updated_at: string;
          attachments: any[];
        };
        Update: {
          id: string;
          application_id: string;
          reference_number: string;
          category: string;
          description: string;
          department: string;
          status: string;
          created_at: string;
          updated_at: string;
          attachments: any[];
        };
      };
      documents: {
        Row: {
          id: string;
          name: string;
          type: string;
          size: number;
          status: string;
          uploaded_at: string;
          category: string;
          extracted_data: any;
        };
        Insert: {
          id: string;
          name: string;
          type: string;
          size: number;
          status: string;
          uploaded_at: string;
          category: string;
          extracted_data: any;
        };
        Update: {
          id: string;
          name: string;
          type: string;
          size: number;
          status: string;
          uploaded_at: string;
          category: string;
          extracted_data: any;
        };
      };
      approval_requests: {
        Row: {
          id: string;
          service: string;
          service_description: string;
          department: {
            name: string;
            code: string;
            jurisdiction: string;
            contact_email: string;
            contact_phone: string;
          };
          portal: {
            name: string;
            url: string;
            last_verified: string;
          };
          applicant: {
            name: string;
            date_of_birth: string;
            gender: string;
            email: string;
            phone: string;
            address: string;
            aadhaar_last_4: string;
          };
          documents: any[];
          form_fields: any[];
          created_at: string;
        };
        Insert: {
          id: string;
          service: string;
          service_description: string;
          department: {
            name: string;
            code: string;
            jurisdiction: string;
            contact_email: string;
            contact_phone: string;
          };
          portal: {
            name: string;
            url: string;
            last_verified: string;
          };
          applicant: {
            name: string;
            date_of_birth: string;
            gender: string;
            email: string;
            phone: string;
            address: string;
            aadhaar_last_4: string;
          };
          documents: any[];
          form_fields: any[];
          created_at: string;
        };
        Update: {
          id: string;
          service: string;
          service_description: string;
          department: {
            name: string;
            code: string;
            jurisdiction: string;
            contact_email: string;
            contact_phone: string;
          };
          portal: {
            name: string;
            url: string;
            last_verified: string;
          };
          applicant: {
            name: string;
            date_of_birth: string;
            gender: string;
            email: string;
            phone: string;
            address: string;
            aadhaar_last_4: string;
          };
          documents: any[];
          form_fields: any[];
          created_at: string;
        };
      };
      approval_results: {
        Row: {
          reference_number: string;
          submitted_at: string;
          next_steps: string[];
        };
        Insert: {
          reference_number: string;
          submitted_at: string;
          next_steps: string[];
        };
        Update: {
          reference_number: string;
          submitted_at: string;
          next_steps: string[];
        };
      };
    };
    Views: {};
    Functions: {};
    Enums: {};
    CompositeTypes: {};
  };
};