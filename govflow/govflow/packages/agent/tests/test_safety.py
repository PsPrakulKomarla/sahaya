"""Tests for SafetyPolicyEngine and ApprovalService."""
import pytest
from datetime import datetime, timedelta
from packages.agent.safety.engine import (
    SafetyDecisionType,
    SafetyPolicyEngine,
)
from packages.agent.safety.approval import ApprovalService
from packages.agent.errors import ApprovalExpired


class TestSafetyPolicyEngine:
    def test_safe_action_allowed(self):
        engine = SafetyPolicyEngine()
        decision = engine.evaluate("READ_PAGE")
        assert decision.decision == SafetyDecisionType.ALLOW

    def test_sensitive_action_requires_approval(self):
        engine = SafetyPolicyEngine()
        decision = engine.evaluate("SUBMIT_APPLICATION")
        assert decision.decision == SafetyDecisionType.REQUIRE_APPROVAL

    def test_sensitive_action_with_valid_approval(self):
        engine = SafetyPolicyEngine()
        decision = engine.evaluate(
            "SUBMIT_APPLICATION",
            has_approval=True,
            approval_valid=True,
        )
        assert decision.decision == SafetyDecisionType.ALLOW

    def test_sensitive_action_with_expired_approval(self):
        engine = SafetyPolicyEngine()
        decision = engine.evaluate(
            "SUBMIT_APPLICATION",
            has_approval=True,
            approval_valid=False,
        )
        assert decision.decision == SafetyDecisionType.REQUIRE_APPROVAL

    def test_denied_action(self):
        engine = SafetyPolicyEngine(additional_denied={"BLOCKED_ACTION"})
        decision = engine.evaluate("BLOCKED_ACTION")
        assert decision.decision == SafetyDecisionType.DENY

    def test_is_sensitive(self):
        engine = SafetyPolicyEngine()
        assert engine.is_sensitive("SUBMIT_APPLICATION")
        assert engine.is_sensitive("MAKE_PAYMENT")
        assert not engine.is_sensitive("READ_PAGE")

    def test_register_sensitive(self):
        engine = SafetyPolicyEngine()
        engine.register_sensitive("CUSTOM_ACTION")
        assert engine.is_sensitive("CUSTOM_ACTION")

    def test_all_sensitive_actions(self):
        engine = SafetyPolicyEngine()
        actions = engine.get_sensitive_actions()
        assert "SUBMIT_APPLICATION" in actions
        assert "SUBMIT_GRIEVANCE" in actions
        assert "MAKE_PAYMENT" in actions
        assert "UPDATE_RECORD" in actions
        assert "DELETE_DATA" in actions

    def test_grievance_requires_approval(self):
        engine = SafetyPolicyEngine()
        decision = engine.evaluate("SUBMIT_GRIEVANCE")
        assert decision.decision == SafetyDecisionType.REQUIRE_APPROVAL

    def test_payment_requires_approval(self):
        engine = SafetyPolicyEngine()
        decision = engine.evaluate("MAKE_PAYMENT")
        assert decision.decision == SafetyDecisionType.REQUIRE_APPROVAL


class TestApprovalService:
    def test_create_approval(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
            summary="Submit income certificate",
        )
        assert request.user_id == "user-1"
        assert request.action_type == "SUBMIT_APPLICATION"
        assert request.status == "pending"
        assert request.expires_at is not None

    def test_approve(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        approved = service.approve(request.id)
        assert approved.status == "approved"
        assert approved.approved_at is not None

    def test_reject(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        rejected = service.reject(request.id)
        assert rejected.status == "rejected"
        assert rejected.rejected_at is not None

    def test_reject_non_pending_fails(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        service.approve(request.id)
        with pytest.raises(ValueError, match="not pending"):
            service.reject(request.id)

    def test_approve_nonexistent_fails(self):
        service = ApprovalService()
        with pytest.raises(ValueError, match="not found"):
            service.approve("nonexistent-id")

    def test_validate_approval(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        assert not service.validate_approval(request.id)

        service.approve(request.id)
        assert service.validate_approval(request.id)

    def test_approval_expiration(self):
        service = ApprovalService(approval_ttl_minutes=0)
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        request.expires_at = datetime.utcnow() - timedelta(seconds=1)
        assert request.is_expired()

    def test_expired_approval_rejects(self):
        service = ApprovalService(approval_ttl_minutes=0)
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        request.expires_at = datetime.utcnow() - timedelta(seconds=1)
        with pytest.raises(ApprovalExpired):
            service.approve(request.id)

    def test_has_pending_approval(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        found = service.has_pending_approval("user-1", "SUBMIT_APPLICATION")
        assert found is not None
        assert found.id == request.id

    def test_no_duplicate_pending(self):
        service = ApprovalService()
        service.create_approval(user_id="user-1", action_type="SUBMIT_APPLICATION")
        service.create_approval(user_id="user-1", action_type="SUBMIT_APPLICATION")
        found = service.has_pending_approval("user-1", "SUBMIT_APPLICATION")
        assert found is not None

    def test_get_user_approvals(self):
        service = ApprovalService()
        service.create_approval(user_id="user-1", action_type="SUBMIT_APPLICATION")
        service.create_approval(user_id="user-1", action_type="MAKE_PAYMENT")
        service.create_approval(user_id="user-2", action_type="SUBMIT_APPLICATION")

        user1 = service.get_user_approvals("user-1")
        assert len(user1) == 2

        user1_submits = service.get_user_approvals("user-1", status="pending")
        assert len(user1_submits) == 2

    def test_generate_summary(self):
        service = ApprovalService()
        summary = service.generate_summary(
            action_type="SUBMIT_APPLICATION",
            service_name="Income Certificate",
            department="Revenue",
            documents=["Identity Proof", "Address Proof"],
            fields={"name": "REDACTED", "state": "Karnataka"},
        )
        assert "SUBMIT_APPLICATION" in summary
        assert "Income Certificate" in summary

    def test_expire(self):
        service = ApprovalService()
        request = service.create_approval(
            user_id="user-1",
            action_type="SUBMIT_APPLICATION",
        )
        expired = service.expire(request.id)
        assert expired.status == "expired"
