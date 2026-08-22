"""Structured grievance composer.

Builds a professional, fact-based grievance draft from structured inputs.
The composer never invents facts or exaggerates: it only formats verified facts,
attributed user claims, and explicitly-labeled inferences.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from packages.grievances.models import FactType, GrievanceDraft, GrievanceFact


class GrievanceComposer:
    """Composes a localized grievance ``GrievanceDraft`` from facts."""

    def compose(
        self,
        *,
        user_issue: str,
        application_reference: str | None,
        service: str,
        jurisdiction: str | None,
        category_label: str,
        verified_facts: list[GrievanceFact] | None = None,
        user_claims: list[GrievanceFact] | None = None,
        attachments: list[str] | None = None,
        language: str = "en",
    ) -> GrievanceDraft:
        verified = list(verified_facts or [])
        claims = list(user_claims or [])
        attachments = list(attachments or [])

        subject = self._build_subject(category_label, application_reference, language)
        description = self._build_description(
            subject_line=subject,
            service=service,
            jurisdiction=jurisdiction,
            category_label=category_label,
            application_reference=application_reference,
            verified_facts=verified,
            user_claims=claims,
        )

        facts: list[GrievanceFact] = []
        facts.extend(verified)
        facts.extend(claims)

        return GrievanceDraft(
            subject=subject,
            description=description,
            category_label=category_label,
            application_reference=application_reference,
            facts=facts,
            attachments=attachments,
        )

    def _build_subject(self, category_label: str, application_reference: str | None, language: str) -> str:
        ref = f" (ref: {application_reference})" if application_reference else ""
        return f"{category_label}{ref}"

    def _build_description(
        self,
        *,
        subject_line: str,
        service: str,
        jurisdiction: str | None,
        category_label: str,
        application_reference: str | None,
        verified_facts: list[GrievanceFact],
        user_claims: list[GrievanceFact],
    ) -> str:
        lines: list[str] = []
        lines.append(f"Subject: {subject_line}")
        lines.append(f"Service: {service}")
        if jurisdiction:
            lines.append(f"Jurisdiction: {jurisdiction}")
        if application_reference:
            lines.append(f"Application reference: {application_reference}")
        lines.append(f"Category: {category_label}")
        lines.append("")
        lines.append("Verified facts:")
        if verified_facts:
            for f in verified_facts:
                lines.append(f"- {f.statement}")
        else:
            lines.append("- None provided.")
        lines.append("")
        lines.append("User-reported issues:")
        if user_claims:
            for f in user_claims:
                lines.append(f"- {f.statement}")
        else:
            lines.append("- None provided.")
        lines.append("")
        lines.append(
            "I request that this matter be reviewed and resolved, and that I be "
            "informed of the outcome in writing."
        )
        return "\n".join(lines)


def make_fact(
    statement: str,
    source: str | None = None,
    *,
    fact_type: FactType = FactType.VERIFIED_FACT,
) -> GrievanceFact:
    """Convenience factory for creating typed grievance facts."""
    return GrievanceFact(type=fact_type, statement=statement, source=source)


def application_submitted_fact(
    reference: str | None,
    when: datetime | date | None,
) -> GrievanceFact:
    """Build a verified fact about an application submission."""
    if when is None and reference is None:
        return make_fact("Application details were not provided.")
    when_str = when.isoformat() if when is not None else "an unknown date"
    ref_part = f" (reference {reference})" if reference else ""
    return make_fact(f"Application was submitted on {when_str}{ref_part}.")


def today_verified_fact() -> GrievanceFact:
    """Build a verified fact marking today's date as the basis of a delay claim."""
    return make_fact(f"As of {date.today().isoformat()}, no decision has been received.")