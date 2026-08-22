"""Grievance categories — declarations and multilingual keyword detection.

Categories are data-driven (registry style), so new categories can be added
without modifying ``GrievanceService`` or the API layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from packages.grievances.models import GrievanceCategory


@dataclass(frozen=True)
class GrievanceCategoryDefinition:
    category: GrievanceCategory
    label: str
    description: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    keywords_kn: tuple[str, ...] = field(default_factory=tuple)
    keywords_hi: tuple[str, ...] = field(default_factory=tuple)


CATEGORY_DEFINITIONS: dict[GrievanceCategory, GrievanceCategoryDefinition] = {
    GrievanceCategory.APPLICATION_DELAY: GrievanceCategoryDefinition(
        category=GrievanceCategory.APPLICATION_DELAY,
        label="Application Delayed",
        description="The application has not been processed within the expected timeframe.",
        keywords=("delay", "delayed", "pending", "stuck", "waiting", "no update", "overdue"),
        keywords_kn=("ವಿಳಂಬ", "ಬಾಕಿ", "ನಿರೀಕ್ಷೆ", "ಇನ್ನೂ"),
        keywords_hi=("विलंब", "लंबित", "इंतजार", "अभी तक"),
    ),
    GrievanceCategory.APPLICATION_REJECTION: GrievanceCategoryDefinition(
        category=GrievanceCategory.APPLICATION_REJECTION,
        label="Application Rejected",
        description="The application was rejected, potentially with a reason that needs review.",
        keywords=("rejected", "rejection", "denied", "refused", "not approved"),
        keywords_kn=("ನಿರಾಕರಿಸ", "ತಿರಸ್ಕರಿಸ"),
        keywords_hi=("अस्वीकार", "खारिज", "नामंजूर"),
    ),
    GrievanceCategory.DOCUMENT_ISSUE: GrievanceCategoryDefinition(
        category=GrievanceCategory.DOCUMENT_ISSUE,
        label="Document Issue",
        description="Problems with submitted documents, such as rejection or loss.",
        keywords=("document", "attachment", "upload", "proof", "file"),
        keywords_kn=("ದಾಖಲೆ", "ಫೈಲ್", "ಅಪ್‌ಲೋಡ್"),
        keywords_hi=("दस्तावेज़", "फ़ाइल", "अपलोड"),
    ),
    GrievanceCategory.INCORRECT_INFORMATION: GrievanceCategoryDefinition(
        category=GrievanceCategory.INCORRECT_INFORMATION,
        label="Incorrect Information",
        description="The official record or application contains incorrect information.",
        keywords=("wrong", "incorrect", "mistake", "error", "spelled", "incorrectly"),
        keywords_kn=("ತಪ್ಪು", "ಅಸಮಂಜಸ"),
        keywords_hi=("गलत", "अशुद्ध"),
    ),
    GrievanceCategory.PAYMENT_ISSUE: GrievanceCategoryDefinition(
        category=GrievanceCategory.PAYMENT_ISSUE,
        label="Payment Issue",
        description="A payment was charged, failed, or not reflected.",
        keywords=("payment", "paid", "fee", "charge", "refund", "transaction"),
        keywords_kn=("ಪಾವತಿ", "ಫೀ", "ಹಣ"),
        keywords_hi=("भुगतान", "शुल्क", "पैसा"),
    ),
    GrievanceCategory.PORTAL_PROBLEM: GrievanceCategoryDefinition(
        category=GrievanceCategory.PORTAL_PROBLEM,
        label="Portal Problem",
        description="Technical problem with the government portal itself.",
        keywords=("portal", "website", "site", "login", "technical", "error page", "server error"),
        keywords_kn=("ವೆಬ್", "ಲಾಗಿನ್", "ತಂತ್ರ"),
        keywords_hi=("पोर्टल", "वेब", "लॉगिन"),
    ),
    GrievanceCategory.SERVICE_UNAVAILABLE: GrievanceCategoryDefinition(
        category=GrievanceCategory.SERVICE_UNAVAILABLE,
        label="Service Unavailable",
        description="The service is unavailable or not offered in the user's area.",
        keywords=("unavailable", "not available", "not listed", "no service", "not offered"),
        keywords_kn=("ಲಭ್ಯವಿಲ"),
        keywords_hi=("अनुपलब्ध", "उपलब्ध नहीं"),
    ),
    GrievanceCategory.OTHER: GrievanceCategoryDefinition(
        category=GrievanceCategory.OTHER,
        label="Other",
        description="Any other grievance that does not fit an existing category.",
    ),
}


class GrievanceCategoryRegistry:
    """Registry of grievance categories with multilingual detection."""

    def __init__(
        self,
        definitions: dict[GrievanceCategory, GrievanceCategoryDefinition] | None = None,
    ) -> None:
        self._definitions = dict(definitions or CATEGORY_DEFINITIONS)

    def all(self) -> list[GrievanceCategoryDefinition]:
        return list(self._definitions.values())

    def get(self, category: GrievanceCategory) -> GrievanceCategoryDefinition | None:
        return self._definitions.get(category)

    def detect(self, text: str, language: str = "en") -> GrievanceCategory:
        """Classify free-text into a category using multilingual keywords."""
        lowered = (text or "").lower()
        keyword_attr = {
            "en": "keywords",
            "kn": "keywords_kn",
            "hi": "keywords_hi",
        }.get(language, "keywords")
        best: GrievanceCategory = GrievanceCategory.OTHER
        best_score = 0
        for definition in self._definitions.values():
            keywords = getattr(definition, keyword_attr, ())
            score = sum(1 for kw in keywords if kw in lowered)
            if score > best_score:
                best_score = score
                best = definition.category
        if best_score == 0 and language in {"kn", "hi"}:
            for definition in self._definitions.values():
                score = sum(1 for kw in definition.keywords if kw in lowered)
                if score > best_score:
                    best_score = score
                    best = definition.category
        return best


default_registry = GrievanceCategoryRegistry()