"""Tests for the AgentStateMachine."""
import pytest
from packages.agent.planner.state_machine import (
    AgentState,
    AgentStateMachine,
    StateTransitionError,
)


class TestStateMachineValidTransitions:
    def test_created_to_understanding(self):
        sm = AgentStateMachine()
        assert sm.state == AgentState.CREATED

        event = sm.transition(AgentState.UNDERSTANDING, "Start")
        assert sm.state == AgentState.UNDERSTANDING
        assert event.from_state == AgentState.CREATED
        assert event.to_state == AgentState.UNDERSTANDING

    def test_full_happy_path(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.VERIFYING)
        sm.transition(AgentState.COMPLETED)

        assert sm.state == AgentState.COMPLETED
        assert sm.is_terminal()

    def test_validating_to_waiting_for_documents(self):
        sm = AgentStateMachine(AgentState.VALIDATING)
        sm.transition(AgentState.WAITING_FOR_DOCUMENTS)
        assert sm.state == AgentState.WAITING_FOR_DOCUMENTS

    def test_validating_to_executing(self):
        sm = AgentStateMachine(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        assert sm.state == AgentState.EXECUTING

    def test_executing_to_waiting_for_approval(self):
        sm = AgentStateMachine(AgentState.EXECUTING)
        sm.transition(AgentState.WAITING_FOR_APPROVAL)
        assert sm.state == AgentState.WAITING_FOR_APPROVAL

    def test_executing_to_recovery(self):
        sm = AgentStateMachine(AgentState.EXECUTING)
        sm.transition(AgentState.RECOVERY)
        assert sm.state == AgentState.RECOVERY

    def test_approval_to_executing(self):
        sm = AgentStateMachine(AgentState.WAITING_FOR_APPROVAL)
        sm.transition(AgentState.EXECUTING)
        assert sm.state == AgentState.EXECUTING

    def test_approval_to_cancelled(self):
        sm = AgentStateMachine(AgentState.WAITING_FOR_APPROVAL)
        sm.transition(AgentState.CANCELLED)
        assert sm.state == AgentState.CANCELLED
        assert sm.is_terminal()

    def test_recovery_to_executing(self):
        sm = AgentStateMachine(AgentState.RECOVERY)
        sm.transition(AgentState.EXECUTING)
        assert sm.state == AgentState.EXECUTING

    def test_recovery_to_waiting_for_user(self):
        sm = AgentStateMachine(AgentState.RECOVERY)
        sm.transition(AgentState.WAITING_FOR_USER)
        assert sm.state == AgentState.WAITING_FOR_USER

    def test_recovery_to_failed(self):
        sm = AgentStateMachine(AgentState.RECOVERY)
        sm.transition(AgentState.FAILED)
        assert sm.state == AgentState.FAILED
        assert sm.is_terminal()

    def test_tracking_to_completed(self):
        sm = AgentStateMachine(AgentState.TRACKING)
        sm.transition(AgentState.COMPLETED)
        assert sm.state == AgentState.COMPLETED


class TestStateMachineInvalidTransitions:
    def test_created_to_executing_fails(self):
        sm = AgentStateMachine()
        with pytest.raises(StateTransitionError) as exc_info:
            sm.transition(AgentState.EXECUTING)
        assert exc_info.value.current_state == AgentState.CREATED
        assert exc_info.value.target_state == AgentState.EXECUTING

    def test_completed_is_terminal(self):
        sm = AgentStateMachine(AgentState.COMPLETED)
        with pytest.raises(StateTransitionError):
            sm.transition(AgentState.EXECUTING)

    def test_failed_is_terminal(self):
        sm = AgentStateMachine(AgentState.FAILED)
        with pytest.raises(StateTransitionError):
            sm.transition(AgentState.CREATED)

    def test_cancelled_is_terminal(self):
        sm = AgentStateMachine(AgentState.CANCELLED)
        with pytest.raises(StateTransitionError):
            sm.transition(AgentState.EXECUTING)

    def test_invalid_transition_preserves_state(self):
        sm = AgentStateMachine(AgentState.CREATED)
        try:
            sm.transition(AgentState.COMPLETED)
        except StateTransitionError:
            pass
        assert sm.state == AgentState.CREATED

    def test_error_has_allowed_transitions(self):
        sm = AgentStateMachine(AgentState.CREATED)
        with pytest.raises(StateTransitionError) as exc_info:
            sm.transition(AgentState.COMPLETED)
        allowed = exc_info.value.allowed_transitions
        assert AgentState.UNDERSTANDING in allowed

    def test_error_to_dict(self):
        sm = AgentStateMachine(AgentState.CREATED)
        with pytest.raises(StateTransitionError) as exc_info:
            sm.transition(AgentState.COMPLETED)
        d = exc_info.value.to_dict()
        assert d["current_state"] == "CREATED"
        assert d["target_state"] == "COMPLETED"


class TestStateMachineRecovery:
    def test_force_state(self):
        sm = AgentStateMachine(AgentState.EXECUTING)
        event = sm.force_state(AgentState.CANCELLED, "user cancel")
        assert sm.state == AgentState.CANCELLED
        assert "[FORCED]" in event.reason

    def test_can_transition(self):
        sm = AgentStateMachine()
        assert sm.can_transition(AgentState.UNDERSTANDING)
        assert not sm.can_transition(AgentState.COMPLETED)

    def test_get_allowed_transitions(self):
        sm = AgentStateMachine()
        allowed = sm.get_allowed_transitions()
        assert AgentState.UNDERSTANDING in allowed


class TestStateMachineHistory:
    def test_history_recorded(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)

        history = sm.history
        assert len(history) == 2
        assert history[0].to_state == AgentState.UNDERSTANDING
        assert history[1].to_state == AgentState.RESOLVING_SERVICE

    def test_get_state_history(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)

        history = sm.get_state_history()
        assert len(history) == 1
        assert history[0]["from"] == "CREATED"
        assert history[0]["to"] == "UNDERSTANDING"
        assert "timestamp" in history[0]


class TestStateMachineCallbacks:
    def test_callback_called(self):
        sm = AgentStateMachine()
        transitions = []
        sm.on_transition(lambda f, t, r: transitions.append((f, t)))

        sm.transition(AgentState.UNDERSTANDING)
        assert len(transitions) == 1
        assert transitions[0] == (AgentState.CREATED, AgentState.UNDERSTANDING)
