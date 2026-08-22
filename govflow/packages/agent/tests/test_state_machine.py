import pytest
from packages.agent.state_machine.machine import AgentStateMachine, VALID_TRANSITIONS
from packages.agent.models.tasks import AgentState
from packages.agent.models.errors import InvalidStateTransition


class TestAgentStateMachine:
    def test_initial_state(self):
        sm = AgentStateMachine()
        assert sm.state == AgentState.CREATED

    def test_custom_initial_state(self):
        sm = AgentStateMachine(initial_state=AgentState.EXECUTING)
        assert sm.state == AgentState.EXECUTING

    def test_valid_transition(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        assert sm.state == AgentState.UNDERSTANDING

    def test_invalid_transition(self):
        sm = AgentStateMachine()
        with pytest.raises(InvalidStateTransition):
            sm.transition(AgentState.COMPLETED)

    def test_can_transition(self):
        sm = AgentStateMachine()
        assert sm.can_transition(AgentState.UNDERSTANDING) is True
        assert sm.can_transition(AgentState.COMPLETED) is False

    def test_full_flow(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.COMPLETED)
        assert sm.state == AgentState.COMPLETED

    def test_history(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)
        assert len(sm.history) == 2
        assert sm.history[0] == (AgentState.CREATED, AgentState.UNDERSTANDING)
        assert sm.history[1] == (AgentState.UNDERSTANDING, AgentState.RESOLVING_SERVICE)

    def test_reset(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.reset()
        assert sm.state == AgentState.CREATED
        assert len(sm.history) == 0

    def test_cancellation(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.CANCELLED)
        assert sm.state == AgentState.CANCELLED

    def test_failure_from_executing(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.FAILED)
        assert sm.state == AgentState.FAILED

    def test_recovery_from_failure(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.FAILED)
        sm.transition(AgentState.RECOVERY)
        assert sm.state == AgentState.RECOVERY

    def test_waiting_for_approval(self):
        sm = AgentStateMachine()
        sm.transition(AgentState.UNDERSTANDING)
        sm.transition(AgentState.RESOLVING_SERVICE)
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.WAITING_FOR_APPROVAL)
        assert sm.state == AgentState.WAITING_FOR_APPROVAL

    def test_all_transitions_defined(self):
        for state in AgentState:
            assert state in VALID_TRANSITIONS
