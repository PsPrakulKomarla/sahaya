from typing import Dict, Set, Tuple
from packages.agent.models.tasks import AgentState
from packages.agent.models.errors import InvalidStateTransition


VALID_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.CREATED: {AgentState.UNDERSTANDING},
    AgentState.UNDERSTANDING: {AgentState.RESOLVING_SERVICE, AgentState.FAILED, AgentState.CANCELLED},
    AgentState.RESOLVING_SERVICE: {AgentState.PLANNING, AgentState.FAILED, AgentState.CANCELLED},
    AgentState.PLANNING: {AgentState.VALIDATING, AgentState.FAILED, AgentState.CANCELLED},
    AgentState.VALIDATING: {
        AgentState.WAITING_FOR_DOCUMENTS,
        AgentState.EXECUTING,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.WAITING_FOR_DOCUMENTS: {
        AgentState.EXECUTING,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.EXECUTING: {
        AgentState.WAITING_FOR_APPROVAL,
        AgentState.VERIFYING,
        AgentState.RECOVERY,
        AgentState.SUBMITTING,
        AgentState.TRACKING,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.WAITING_FOR_APPROVAL: {
        AgentState.EXECUTING,
        AgentState.SUBMITTING,
        AgentState.CANCELLED,
        AgentState.FAILED,
    },
    AgentState.SUBMITTING: {
        AgentState.VERIFYING,
        AgentState.RECOVERY,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.VERIFYING: {
        AgentState.TRACKING,
        AgentState.COMPLETED,
        AgentState.RECOVERY,
        AgentState.FAILED,
    },
    AgentState.TRACKING: {
        AgentState.COMPLETED,
        AgentState.RECOVERY,
        AgentState.FAILED,
    },
    AgentState.COMPLETED: set(),
    AgentState.FAILED: {AgentState.RECOVERY, AgentState.CANCELLED},
    AgentState.CANCELLED: set(),
    AgentState.RECOVERY: {
        AgentState.EXECUTING,
        AgentState.WAITING_FOR_USER,
        AgentState.FAILED,
    },
    AgentState.WAITING_FOR_USER: {
        AgentState.EXECUTING,
        AgentState.CANCELLED,
    },
}


class AgentStateMachine:
    """Controls agent state transitions with validation."""

    def __init__(self, initial_state: AgentState = AgentState.CREATED):
        self._state = initial_state
        self._history: list[Tuple[AgentState, AgentState]] = []

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def history(self) -> list[Tuple[AgentState, AgentState]]:
        return list(self._history)

    def can_transition(self, new_state: AgentState) -> bool:
        return new_state in VALID_TRANSITIONS.get(self._state, set())

    def transition(self, new_state: AgentState) -> None:
        if not self.can_transition(new_state):
            raise InvalidStateTransition(self._state.value, new_state.value)
        old_state = self._state
        self._state = new_state
        self._history.append((old_state, new_state))

    def reset(self, state: AgentState = AgentState.CREATED) -> None:
        self._state = state
        self._history.clear()
