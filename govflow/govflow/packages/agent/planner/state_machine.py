"""AgentStateMachine controls the lifecycle of an agent task.

The state machine enforces legal transitions and rejects invalid ones.
It never silently changes state.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from packages.agent.errors import InvalidStateTransition


class AgentState(str, Enum):
    """All possible states of an agent task."""
    CREATED = "CREATED"
    UNDERSTANDING = "UNDERSTANDING"
    RESOLVING_SERVICE = "RESOLVING_SERVICE"
    PLANNING = "PLANNING"
    VALIDATING = "VALIDATING"
    WAITING_FOR_DOCUMENTS = "WAITING_FOR_DOCUMENTS"
    EXECUTING = "EXECUTING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    SUBMITTING = "SUBMITTING"
    VERIFYING = "VERIFYING"
    TRACKING = "TRACKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECOVERY = "RECOVERY"
    WAITING_FOR_USER = "WAITING_FOR_USER"


class StateTransition(BaseModel):
    """Definition of a valid state transition."""
    from_state: AgentState
    to_state: AgentState
    description: str = ""


class StateChangeEvent(BaseModel):
    """Record of a state change."""
    from_state: AgentState
    to_state: AgentState
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str = ""


# Define all valid transitions
VALID_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.CREATED: {AgentState.UNDERSTANDING},
    AgentState.UNDERSTANDING: {AgentState.RESOLVING_SERVICE},
    AgentState.RESOLVING_SERVICE: {AgentState.PLANNING},
    AgentState.PLANNING: {AgentState.VALIDATING},
    AgentState.VALIDATING: {
        AgentState.WAITING_FOR_DOCUMENTS,
        AgentState.EXECUTING,
    },
    AgentState.WAITING_FOR_DOCUMENTS: {AgentState.EXECUTING},
    AgentState.EXECUTING: {
        AgentState.WAITING_FOR_APPROVAL,
        AgentState.VERIFYING,
        AgentState.RECOVERY,
    },
    AgentState.WAITING_FOR_APPROVAL: {
        AgentState.EXECUTING,
        AgentState.CANCELLED,
    },
    AgentState.SUBMITTING: {
        AgentState.VERIFYING,
        AgentState.RECOVERY,
        AgentState.COMPLETED,
    },
    AgentState.VERIFYING: {
        AgentState.TRACKING,
        AgentState.COMPLETED,
    },
    AgentState.TRACKING: {AgentState.COMPLETED},
    AgentState.RECOVERY: {
        AgentState.EXECUTING,
        AgentState.WAITING_FOR_USER,
        AgentState.FAILED,
    },
    AgentState.WAITING_FOR_USER: {AgentState.EXECUTING, AgentState.CANCELLED},
    AgentState.COMPLETED: set(),
    AgentState.FAILED: set(),
    AgentState.CANCELLED: set(),
}


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted.

    This is a dedicated exception for the state machine that preserves
    the previous valid state and provides structured error information.
    """

    def __init__(
        self,
        current_state: AgentState,
        target_state: AgentState,
        allowed: Set[AgentState],
    ):
        self.current_state = current_state
        self.target_state = target_state
        self.allowed_transitions = allowed
        self.message = (
            f"Invalid transition: {current_state.value} -> {target_state.value}. "
            f"Allowed: {[s.value for s in allowed]}"
        )
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": "INVALID_STATE_TRANSITION",
            "current_state": self.current_state.value,
            "target_state": self.target_state.value,
            "allowed_transitions": [s.value for s in self.allowed_transitions],
        }


TransitionCallback = Callable[[AgentState, AgentState, str], None]


class AgentStateMachine:
    """Controls the lifecycle of an agent task.

    Enforces valid transitions and records state change history.
    """

    def __init__(self, initial_state: AgentState = AgentState.CREATED):
        self._state = initial_state
        self._history: List[StateChangeEvent] = []
        self._callbacks: List[TransitionCallback] = []
        self._valid_transitions = dict(VALID_TRANSITIONS)

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def history(self) -> List[StateChangeEvent]:
        return list(self._history)

    def on_transition(self, callback: TransitionCallback) -> None:
        """Register a callback for state transitions."""
        self._callbacks.append(callback)

    def can_transition(self, target: AgentState) -> bool:
        """Check if a transition to the target state is valid."""
        return target in self._valid_transitions.get(self._state, set())

    def get_allowed_transitions(self) -> Set[AgentState]:
        """Get the set of states this machine can transition to."""
        return self._valid_transitions.get(self._state, set()).copy()

    def transition(self, target: AgentState, reason: str = "") -> StateChangeEvent:
        """Attempt a state transition.

        Args:
            target: The desired target state.
            reason: Optional reason for the transition.

        Returns:
            The StateChangeEvent recording the transition.

        Raises:
            StateTransitionError: If the transition is not valid.
        """
        allowed = self._valid_transitions.get(self._state, set())

        if target not in allowed:
            raise StateTransitionError(self._state, target, allowed)

        previous = self._state
        self._state = target

        event = StateChangeEvent(
            from_state=previous,
            to_state=target,
            reason=reason,
        )
        self._history.append(event)

        for callback in self._callbacks:
            try:
                callback(previous, target, reason)
            except Exception:
                pass

        return event

    def force_state(self, state: AgentState, reason: str = "forced") -> StateChangeEvent:
        """Force a state change (for recovery/cancellation).

        This bypasses transition validation but is logged.
        Used only for exceptional circumstances like cancellation.
        """
        previous = self._state
        self._state = state

        event = StateChangeEvent(
            from_state=previous,
            to_state=state,
            reason=f"[FORCED] {reason}",
        )
        self._history.append(event)
        return event

    def is_terminal(self) -> bool:
        """Check if the current state is terminal."""
        return self._state in {AgentState.COMPLETED, AgentState.FAILED, AgentState.CANCELLED}

    def get_state_history(self) -> List[dict]:
        """Return the full state change history as dicts."""
        return [
            {
                "from": e.from_state.value,
                "to": e.to_state.value,
                "timestamp": e.timestamp.isoformat(),
                "reason": e.reason,
            }
            for e in self._history
        ]
