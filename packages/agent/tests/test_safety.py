import pytest
from packages.agent.safety.engine import SafetyPolicyEngine, SafetyDecision, SENSITIVE_ACTIONS
from packages.agent.models.tasks import StepType


class TestSafetyPolicyEngine:
    @pytest.fixture
    def engine(self):
        return SafetyPolicyEngine()

    def test_safe_action(self, engine):
        decision = engine.evaluate(StepType.DISCOVER_SERVICE)
        assert decision == SafetyDecision.ALLOW

    def test_sensitive_action_requires_approval(self, engine):
        decision = engine.evaluate(StepType.SUBMIT)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_update_record_requires_approval(self, engine):
        decision = engine.evaluate(StepType.UPDATE_RECORD)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_renew_requires_approval(self, engine):
        decision = engine.evaluate(StepType.RENEW)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_raise_grievance_requires_approval(self, engine):
        decision = engine.evaluate(StepType.RAISE_GRIEVANCE)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_with_approval_context(self, engine):
        context = {"has_approval": True, "approval_valid": True}
        decision = engine.evaluate(StepType.SUBMIT, context)
        assert decision == SafetyDecision.ALLOW

    def test_with_invalid_approval(self, engine):
        context = {"has_approval": True, "approval_valid": False}
        decision = engine.evaluate(StepType.SUBMIT, context)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_without_approval(self, engine):
        context = {"has_approval": False}
        decision = engine.evaluate(StepType.SUBMIT, context)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_deny_action(self, engine):
        engine.deny_action(StepType.SUBMIT)
        decision = engine.evaluate(StepType.SUBMIT)
        assert decision == SafetyDecision.DENY

    def test_allow_action_after_deny(self, engine):
        engine.deny_action(StepType.SUBMIT)
        engine.allow_action(StepType.SUBMIT)
        decision = engine.evaluate(StepType.SUBMIT)
        assert decision == SafetyDecision.REQUIRE_APPROVAL

    def test_is_sensitive(self, engine):
        assert engine.is_sensitive(StepType.SUBMIT) is True
        assert engine.is_sensitive(StepType.DISCOVER_SERVICE) is False

    def test_all_sensitive_actions(self):
        assert StepType.SUBMIT in SENSITIVE_ACTIONS
        assert StepType.UPDATE_RECORD in SENSITIVE_ACTIONS
        assert StepType.RENEW in SENSITIVE_ACTIONS
        assert StepType.RAISE_GRIEVANCE in SENSITIVE_ACTIONS

    def test_custom_sensitive_actions(self):
        engine = SafetyPolicyEngine(extra_sensitive={StepType.BROWSER_EXECUTION})
        assert engine.is_sensitive(StepType.BROWSER_EXECUTION) is True
