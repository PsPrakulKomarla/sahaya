import pytest
from packages.agent.recovery.memory import RecoveryMemory, RecoveryRecord, WorkflowUpdate
from packages.agent.recovery.types import (
    FailureType, RecoveryDecision, RecoveryDecisionType, RecoveryLevel,
)


@pytest.fixture
def memory():
    return RecoveryMemory()


def _make_decision(
    decision: RecoveryDecisionType = RecoveryDecisionType.RECOVER,
    confidence: float = 0.9,
    candidate_text: str = "new target",
    candidate_selector: str = "#new-target",
    recovery_level: RecoveryLevel = RecoveryLevel.LEVEL_2_REINSPECT,
) -> RecoveryDecision:
    return RecoveryDecision(
        decision=decision,
        confidence=confidence,
        candidate_text=candidate_text,
        candidate_selector=candidate_selector,
        recovery_level=recovery_level,
    )


class TestRecordRecovery:
    def test_record_successful_recovery(self, memory):
        decision = _make_decision(decision=RecoveryDecisionType.RECOVER)
        record = memory.record_recovery(
            step_id="step_1",
            old_target_text="Submit",
            old_target_role="button",
            failure_type=FailureType.ELEMENT_NOT_FOUND,
            decision=decision,
            page_url="https://example.com/form",
            page_title="Form Page",
        )
        assert record.success is True
        assert record.old_step_id == "step_1"
        assert record.replacement_text == "new target"
        assert memory.total_records == 1
        assert memory.success_rate == 1.0

    def test_record_failed_recovery(self, memory):
        decision = _make_decision(decision=RecoveryDecisionType.ABORT)
        record = memory.record_recovery(
            step_id="step_1",
            old_target_text="Submit",
            old_target_role="button",
            failure_type=FailureType.ELEMENT_NOT_FOUND,
            decision=decision,
        )
        assert record.success is False
        assert memory.total_records == 1
        assert memory.success_rate == 0.0


class TestGetRecords:
    def test_get_records_for_step(self, memory):
        d1 = _make_decision(candidate_text="a")
        d2 = _make_decision(candidate_text="b")
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, d1)
        memory.record_recovery("step_1", "Cancel", "button", FailureType.ELEMENT_CHANGED, d2)
        memory.record_recovery("step_2", "Next", "link", FailureType.TIMEOUT, d1)

        records = memory.get_records_for_step("step_1")
        assert len(records) == 2
        assert all(r.old_step_id == "step_1" for r in records)

    def test_get_successful_replacements(self, memory):
        success = _make_decision(decision=RecoveryDecisionType.RECOVER, candidate_text="replacement_a")
        fail = _make_decision(decision=RecoveryDecisionType.ABORT, candidate_text="replacement_b")
        memory.record_recovery("step_1", "Old", "button", FailureType.ELEMENT_NOT_FOUND, success)
        memory.record_recovery("step_1", "Old", "button", FailureType.ELEMENT_NOT_FOUND, fail)
        memory.record_recovery("step_1", "Old", "button", FailureType.ELEMENT_NOT_FOUND, success)

        replacements = memory.get_successful_replacements("step_1")
        assert len(replacements) == 2
        assert all(r.success is True for r in replacements)


class TestSuggestAlternative:
    def test_suggest_alternative_from_past_recoveries(self, memory):
        decision = _make_decision(
            decision=RecoveryDecisionType.RECOVER,
            confidence=0.8,
            candidate_text="Updated Submit",
        )
        memory.record_recovery("step_1", "Old Submit", "button", FailureType.ELEMENT_NOT_FOUND, decision)

        suggestion = memory.suggest_alternative("step_1", "Submit")
        assert suggestion is not None
        assert suggestion.replacement_text == "Updated Submit"
        assert suggestion.replacement_text == "Updated Submit"

    def test_no_alternative_when_no_past_recoveries(self, memory):
        suggestion = memory.suggest_alternative("step_1", "Submit")
        assert suggestion is None

    def test_no_alternative_when_past_recovery_confidence_too_low(self, memory):
        decision = _make_decision(
            decision=RecoveryDecisionType.RECOVER,
            confidence=0.3,
            candidate_text="Low Confidence",
        )
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, decision)

        suggestion = memory.suggest_alternative("step_1", "Submit")
        assert suggestion is None

    def test_no_alternative_when_same_target_text(self, memory):
        decision = _make_decision(
            decision=RecoveryDecisionType.RECOVER,
            confidence=0.9,
            candidate_text="Same Text",
        )
        memory.record_recovery("step_1", "Same Text", "button", FailureType.ELEMENT_NOT_FOUND, decision)

        suggestion = memory.suggest_alternative("step_1", "Same Text")
        assert suggestion is None


class TestWorkflowUpdate:
    def test_workflow_update_recording(self, memory):
        update = WorkflowUpdate(
            workflow_id="wf_1",
            old_version="v1",
            new_version="v2",
            updated_steps=[{"step_id": "step_1", "action": "click"}],
            reason="Recovery-based update",
            confidence=0.85,
        )
        memory.record_workflow_update(update)

        updates = memory.get_workflow_updates("wf_1")
        assert len(updates) == 1
        assert updates[0].workflow_id == "wf_1"
        assert updates[0].new_version == "v2"

    def test_should_update_workflow_enough_successes(self, memory):
        d1 = _make_decision(decision=RecoveryDecisionType.RECOVER, confidence=0.8)
        d2 = _make_decision(decision=RecoveryDecisionType.RECOVER, confidence=0.9)
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, d1)
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, d2)

        assert memory.should_update_workflow("step_1") is True

    def test_should_not_update_workflow_insufficient_successes(self, memory):
        d1 = _make_decision(decision=RecoveryDecisionType.RECOVER, confidence=0.9)
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, d1)

        assert memory.should_update_workflow("step_1") is False

    def test_should_not_update_workflow_low_confidence(self, memory):
        d1 = _make_decision(decision=RecoveryDecisionType.RECOVER, confidence=0.5)
        d2 = _make_decision(decision=RecoveryDecisionType.RECOVER, confidence=0.6)
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, d1)
        memory.record_recovery("step_1", "Submit", "button", FailureType.ELEMENT_NOT_FOUND, d2)

        assert memory.should_update_workflow("step_1") is False


class TestMetrics:
    def test_success_rate_calculation(self, memory):
        assert memory.success_rate == 0.0

        s = _make_decision(decision=RecoveryDecisionType.RECOVER)
        f = _make_decision(decision=RecoveryDecisionType.ABORT)
        memory.record_recovery("s", "x", "b", FailureType.TIMEOUT, s)
        memory.record_recovery("f1", "x", "b", FailureType.TIMEOUT, f)
        memory.record_recovery("f2", "x", "b", FailureType.TIMEOUT, f)
        memory.record_recovery("f3", "x", "b", FailureType.TIMEOUT, f)
        memory.record_recovery("s2", "x", "b", FailureType.TIMEOUT, s)

        assert memory.success_rate == pytest.approx(0.4)

    def test_summary_output(self, memory):
        s = _make_decision(decision=RecoveryDecisionType.RECOVER, confidence=0.8)
        f = _make_decision(decision=RecoveryDecisionType.ABORT)
        memory.record_recovery("s", "x", "b", FailureType.TIMEOUT, s)
        memory.record_recovery("f", "x", "b", FailureType.TIMEOUT, f)

        update = WorkflowUpdate(workflow_id="wf_1")
        memory.record_workflow_update(update)

        summary = memory.summary()
        assert summary["total_records"] == 2
        assert summary["success_count"] == 1
        assert summary["failure_count"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["workflow_updates"] == 1


class TestRecoveryRecordFields:
    def test_recovery_record_fields_populated_correctly(self, memory):
        decision = _make_decision(
            decision=RecoveryDecisionType.RECOVER,
            confidence=0.75,
            candidate_text="New Button",
            candidate_selector="button.new-submit",
            recovery_level=RecoveryLevel.LEVEL_3_SEMANTIC,
        )
        record = memory.record_recovery(
            step_id="step_1",
            old_target_text="Old Button",
            old_target_role="submit",
            failure_type=FailureType.ELEMENT_CHANGED,
            decision=decision,
            page_url="https://example.com",
            page_title="Test Page",
        )

        assert record.record_id.startswith("rec_step_1_")
        assert record.old_step_id == "step_1"
        assert record.old_target_text == "Old Button"
        assert record.old_target_role == "submit"
        assert record.failure_type == FailureType.ELEMENT_CHANGED
        assert record.replacement_text == "New Button"
        assert record.replacement_selector == "button.new-submit"
        assert record.page_url == "https://example.com"
        assert record.page_title == "Test Page"
        assert record.success is True
        assert record.confidence == 0.75
        assert record.recovery_level == RecoveryLevel.LEVEL_3_SEMANTIC
        assert record.timestamp is not None
