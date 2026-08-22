import pytest
from datetime import datetime
from packages.grievances.models import (
    GrievanceCategory,
    GrievanceFact,
    FactType,
    GrievanceDraft,
)
from packages.grievances.composer import (
    GrievanceComposer,
    make_fact,
    application_submitted_fact,
    today_verified_fact,
)


class TestGrievanceComposer:
    def setup_method(self):
        self.composer = GrievanceComposer()

    def test_compose_basic(self):
        draft = self.composer.compose(
            user_issue="My application is delayed",
            application_reference="APP123",
            service="Income Certificate",
            jurisdiction="Karnataka",
            category_label="Application Delayed",
            verified_facts=[
                GrievanceFact(type=FactType.VERIFIED_FACT, statement="Submitted on 2026-01-01")
            ],
            user_claims=[
                GrievanceFact(type=FactType.USER_CLAIM, statement="No update received")
            ],
        )
        assert isinstance(draft, GrievanceDraft)
        assert draft.subject == "Application Delayed (ref: APP123)"
        assert "Income Certificate" in draft.description
        assert "Karnataka" in draft.description
        assert len(draft.facts) == 2

    def test_compose_without_application_ref(self):
        draft = self.composer.compose(
            user_issue="Service unavailable",
            application_reference=None,
            service="Passport",
            jurisdiction=None,
            category_label="Service Unavailable",
        )
        assert "ref:" not in draft.subject

    def test_compose_with_attachments(self):
        draft = self.composer.compose(
            user_issue="Document issue",
            application_reference="APP123",
            service="Income Certificate",
            jurisdiction="Karnataka",
            category_label="Document Issue",
            attachments=["doc1.pdf", "doc2.pdf"],
        )
        assert "doc1.pdf" in draft.attachments
        assert "doc2.pdf" in draft.attachments

    def test_make_fact(self):
        fact = make_fact("Test statement", source="user", fact_type=FactType.USER_CLAIM)
        assert fact.statement == "Test statement"
        assert fact.source == "user"
        assert fact.type == FactType.USER_CLAIM

    def test_application_submitted_fact_with_date(self):
        fact = application_submitted_fact("REF123", datetime(2026, 1, 15))
        assert "REF123" in fact.statement
        assert "2026-01-15" in fact.statement

    def test_application_submitted_fact_without_date(self):
        fact = application_submitted_fact("REF123", None)
        assert "REF123" in fact.statement
        assert "unknown date" in fact.statement

    def test_today_verified_fact(self):
        fact = today_verified_fact()
        assert "no decision has been received" in fact.statement
        assert datetime.now().strftime("%Y-%m-%d") in fact.statement

    def test_compose_separates_facts_and_claims(self):
        verified = [GrievanceFact(type=FactType.VERIFIED_FACT, statement="Submitted 2026-01-01")]
        claims = [GrievanceFact(type=FactType.USER_CLAIM, statement="No response")]

        draft = self.composer.compose(
            user_issue="Delay",
            application_reference="APP123",
            service="Income Certificate",
            jurisdiction="Karnataka",
            category_label="Application Delayed",
            verified_facts=verified,
            user_claims=claims,
        )

        verified_in_draft = [f for f in draft.facts if f.type == FactType.VERIFIED_FACT]
        claims_in_draft = [f for f in draft.facts if f.type == FactType.USER_CLAIM]

        assert len(verified_in_draft) == 1
        assert len(claims_in_draft) == 1
        assert verified_in_draft[0].statement == "Submitted 2026-01-01"
        assert claims_in_draft[0].statement == "No response"