"""Recovery engine package — layered recovery for browser agent failures."""
from packages.agent.recovery.types import (
    FailureType,
    RecoveryLevel,
    RecoveryDecisionType,
    RecoveryDecision,
    RecoveryEvent,
    RecoveryMetrics,
    SafeActionClassifier,
    IdempotencyCheck,
    SessionRecoveryInfo,
)
from packages.agent.recovery.engine import RecoveryEngine, RecoveryConfiguration

__all__ = [
    "FailureType",
    "RecoveryLevel",
    "RecoveryDecisionType",
    "RecoveryDecision",
    "RecoveryEvent",
    "RecoveryMetrics",
    "SafeActionClassifier",
    "IdempotencyCheck",
    "SessionRecoveryInfo",
    "RecoveryEngine",
    "RecoveryConfiguration",
]
