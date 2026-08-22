import re
from typing import List, Optional, Dict, Any
from packages.documents.base.document_extractor import DocumentExtractor
from packages.documents.base.models import (
    OCRResult,
    ExtractedField,
    FieldSource,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class DefaultDocumentExtractor(DocumentExtractor):
    """Default document field extractor using pattern matching.

    Extracts structured fields from OCR text using regex patterns
    for common Indian document types.
    """

    FIELD_PATTERNS: Dict[str, Dict[str, Any]] = {
        "identity_proof": {
            "name": r"(?:Name|Applicant|Holder)[\s:]+([A-Z][a-zA-Z\s]+)",
            "date_of_birth": r"(?:DOB|Date of Birth|Birth Date)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})",
            "gender": r"(?:Gender|Sex)[\s:]+(Male|Female|Other|M|F)",
            "address": r"(?:Address|Residence)[\s:]+(.+?)(?:\n|$)",
            "aadhaar_number": r"(?:Aadhaar|UID)[\s:]+(\d{4}\s?\d{4}\s?\d{4})",
        },
        "address_proof": {
            "name": r"(?:Name|Consumer|Account)[\s:]+([A-Z][a-zA-Z\s]+)",
            "address": r"(?:Address|Premises|Location)[\s:]+(.+?)(?:\n|$)",
            "bill_date": r"(?:Bill Date|Date|Statement Date)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})",
            "amount": r"(?:Amount|Total|Due)[\s:]+(?:Rs\.?|INR)?\s*([\d,]+\.?\d*)",
        },
        "income_proof": {
            "employee_name": r"(?:Employee Name|Name|Candidate)[\s:]+([A-Z][a-zA-Z\s]+)",
            "employee_id": r"(?:Employee ID|Emp No|ID)[\s:]+([A-Z0-9-]+)",
            "basic_salary": r"(?:Basic Salary|Basic Pay)[\s:]+(?:Rs\.?|INR)?\s*([\d,]+\.?\d*)",
            "net_pay": r"(?:Net Pay|Take Home|In Hand)[\s:]+(?:Rs\.?|INR)?\s*([\d,]+\.?\d*)",
            "month": r"(?:Month|Period|For Month)[\s:]+([A-Za-z]+\s*\d{4})",
        },
        "birth_certificate": {
            "child_name": r"(?:Child Name|Name of Child|Name)[\s:]+([A-Z][a-zA-Z\s]+)",
            "date_of_birth": r"(?:Date of Birth|DOB|Born on)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})",
            "place_of_birth": r"(?:Place of Birth|Born at|Location)[\s:]+(.+?)(?:\n|$)",
            "father_name": r"(?:Father(?:'s)? Name|Father)[\s:]+([A-Z][a-zA-Z\s]+)",
            "mother_name": r"(?:Mother(?:'s)? Name|Mother)[\s:]+([A-Z][a-zA-Z\s]+)",
        },
        "passport": {
            "given_name": r"(?:Given Name|First Name)[\s:]+([A-Z][a-zA-Z\s]+)",
            "surname": r"(?:Surname|Last Name|Family Name)[\s:]+([A-Z]+)",
            "date_of_birth": r"(?:Date of Birth|DOB)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})",
            "place_of_birth": r"(?:Place of Birth|POB)[\s:]+([A-Z][A-Z\s]+)",
            "date_of_issue": r"(?:Date of Issue|Issued)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})",
            "date_of_expiry": r"(?:Date of Expiry|Expiry|Valid Until)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})",
        },
    }

    def supported_document_types(self) -> List[str]:
        return list(self.FIELD_PATTERNS.keys())

    async def extract(
        self,
        ocr_result: OCRResult,
        document_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ExtractedField]:
        """Extract fields from OCR text using pattern matching."""
        text = ocr_result.extracted_text
        patterns = self.FIELD_PATTERNS.get(document_type, {})

        if not patterns:
            logger.info(
                "no_patterns_for_document_type",
                document_type=document_type,
            )
            return self._extract_generic_fields(text, ocr_result.overall_confidence)

        fields: List[ExtractedField] = []
        for field_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                value = self._normalize_value(field_name, value)
                fields.append(
                    ExtractedField(
                        field=field_name,
                        value=value,
                        confidence=ocr_result.overall_confidence,
                        source=FieldSource.OCR,
                        ocr_value=value,
                    )
                )
            else:
                fields.append(
                    ExtractedField(
                        field=field_name,
                        value="",
                        confidence=0.0,
                        source=FieldSource.OCR,
                        ocr_value=None,
                    )
                )

        return fields

    def _normalize_value(self, field_name: str, value: str) -> str:
        """Normalize extracted field values."""
        if "date" in field_name.lower():
            return self._normalize_date(value)
        if "name" in field_name.lower():
            return " ".join(value.split())
        return value

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format."""
        separators = ["/", "-"]
        for sep in separators:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    day, month, year = parts
                    if len(year) == 2:
                        year = "20" + year if int(year) < 50 else "19" + year
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return date_str

    def _extract_generic_fields(self, text: str, confidence: float) -> List[ExtractedField]:
        """Extract generic fields when no specific patterns exist."""
        fields: List[ExtractedField] = []

        name_match = re.search(r"(?:Name)[\s:]+([A-Z][a-zA-Z\s]+)", text, re.IGNORECASE)
        if name_match:
            fields.append(
                ExtractedField(
                    field="name",
                    value=name_match.group(1).strip(),
                    confidence=confidence,
                    source=FieldSource.OCR,
                    ocr_value=name_match.group(1).strip(),
                )
            )

        date_match = re.search(
            r"(?:Date|DOB|Born)[\s:]+(\d{2}[/-]\d{2}[/-]\d{4})", text, re.IGNORECASE
        )
        if date_match:
            fields.append(
                ExtractedField(
                    field="date",
                    value=self._normalize_date(date_match.group(1).strip()),
                    confidence=confidence,
                    source=FieldSource.OCR,
                    ocr_value=date_match.group(1).strip(),
                )
            )

        return fields
