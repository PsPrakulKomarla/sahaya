from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from packages.documents.base.models import (
    DocumentMatchResult,
    DocumentAvailabilityResult,
    ExpiryStatus,
    CrossDocumentCheckResult,
    ExtractedField,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentMatcher:
    """Matches required document types against user's document collection."""

    DOCUMENT_TYPE_COMPATIBILITY: Dict[str, List[str]] = {
        "identity_proof": ["aadhaar", "pan", "passport", "driving_license"],
        "address_proof": ["aadhaar", "address_proof"],
        "income_proof": ["income_proof"],
        "birth_certificate": ["birth_certificate"],
        "passport": ["passport"],
        "driving_licence": ["driving_license"],
        "photograph": ["photograph"],
    }

    def match_documents(
        self,
        required_type: str,
        user_documents: List[Dict[str, Any]],
    ) -> DocumentMatchResult:
        """Match a required document type against user's documents."""
        compatible_types = self.DOCUMENT_TYPE_COMPATIBILITY.get(
            required_type, [required_type]
        )

        best_match: Optional[Dict[str, Any]] = None
        best_score = 0.0

        for doc in user_documents:
            doc_type = doc.get("document_type", "")
            if doc_type in compatible_types:
                score = 1.0
                if doc.get("verification_status") == "verified":
                    score = 1.0
                elif doc.get("verification_status") == "pending":
                    score = 0.8
                elif doc.get("verification_status") == "needs_review":
                    score = 0.6

                if doc.get("ocr_confidence", 0) > 0.8:
                    score *= 1.0
                elif doc.get("ocr_confidence", 0) > 0.5:
                    score *= 0.9

                expiry = self._check_expiry(doc)
                if expiry == ExpiryStatus.EXPIRED:
                    score *= 0.3
                elif expiry == ExpiryStatus.EXPIRING_SOON:
                    score *= 0.7

                if score > best_score:
                    best_score = score
                    best_match = doc

        if best_match:
            return DocumentMatchResult(
                required_type=required_type,
                matched=True,
                document_id=str(best_match.get("id", "")),
                document_type=best_match.get("document_type", ""),
                confidence=best_score,
                expiry_status=self._check_expiry(best_match),
            )

        return DocumentMatchResult(
            required_type=required_type,
            matched=False,
        )

    def check_availability(
        self,
        required_documents: List[Dict[str, Any]],
        user_documents: List[Dict[str, Any]],
    ) -> List[DocumentAvailabilityResult]:
        """Check which required documents are available."""
        results: List[DocumentAvailabilityResult] = []

        for req in required_documents:
            req_type = req.get("document_type", "")
            display_name = req.get("display_name", req_type)
            mandatory = req.get("mandatory", True)

            match = self.match_documents(req_type, user_documents)

            results.append(
                DocumentAvailabilityResult(
                    required_type=req_type,
                    display_name=display_name,
                    mandatory=mandatory,
                    available=match.matched,
                    matching_documents=[match.document_id] if match.document_id else [],
                    expiry_status=match.expiry_status,
                )
            )

        return results

    def _check_expiry(self, document: Dict[str, Any]) -> ExpiryStatus:
        """Check document expiry status."""
        expires_at = document.get("expires_at")
        if not expires_at:
            return ExpiryStatus.UNKNOWN

        try:
            if isinstance(expires_at, str):
                expiry_date = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            else:
                expiry_date = expires_at

            now = datetime.now(timezone.utc)
            if expiry_date < now:
                return ExpiryStatus.EXPIRED

            days_until_expiry = (expiry_date - now).days
            if days_until_expiry < 30:
                return ExpiryStatus.EXPIRING_SOON

            return ExpiryStatus.VALID
        except (ValueError, TypeError):
            return ExpiryStatus.UNKNOWN

    def check_cross_document_consistency(
        self,
        documents_fields: List[List[ExtractedField]],
    ) -> CrossDocumentCheckResult:
        """Check consistency of fields across multiple documents."""
        field_values: Dict[str, List[str]] = {}

        for doc_fields in documents_fields:
            for field in doc_fields:
                if field.value and field.verified:
                    if field.field not in field_values:
                        field_values[field.field] = []
                    field_values[field.field].append(str(field.value))

        discrepancies: List[Dict[str, Any]] = []
        checked_fields: List[str] = []

        for field_name, values in field_values.items():
            if len(values) > 1:
                checked_fields.append(field_name)
                unique_values = list(set(v.strip().lower() for v in values))
                if len(unique_values) > 1:
                    discrepancies.append(
                        {
                            "field": field_name,
                            "values": values,
                            "issue": "POSSIBLE_NAME_MISMATCH"
                            if "name" in field_name.lower()
                            else "VALUE_MISMATCH",
                        }
                    )

        return CrossDocumentCheckResult(
            consistent=len(discrepancies) == 0,
            discrepancies=discrepancies,
            checked_fields=checked_fields,
        )
