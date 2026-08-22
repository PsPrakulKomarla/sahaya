"""LiveExecutionMode — MOCK/TEST/LIVE modes with safety gates.

LIVE mode must require explicit configuration.
Never accidentally execute a real workflow from a unit test.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from packages.agent.executor.context import Permission
from packages.agent.safety.domain import DomainAllowlist, NavigationDecision


class ExecutionMode(str, Enum):
    MOCK = "MOCK"
    TEST = "TEST"
    LIVE = "LIVE"


class LiveSafetyGate(BaseModel):
    service_verified: bool = False
    domain_verified: bool = False
    workflow_version_verified: bool = False
    browser_provider_verified: bool = False
    safety_policy_loaded: bool = False
    human_approval_available: bool = False
    user_authenticated: bool = False
    sensitive_action_gate_enabled: bool = False

    def all_passed(self) -> bool:
        return all([
            self.service_verified,
            self.domain_verified,
            self.workflow_version_verified,
            self.browser_provider_verified,
            self.safety_policy_loaded,
            self.human_approval_available,
            self.user_authenticated,
            self.sensitive_action_gate_enabled,
        ])

    def failures(self) -> List[str]:
        failing = []
        checks = {
            "service_verified": self.service_verified,
            "domain_verified": self.domain_verified,
            "workflow_version_verified": self.workflow_version_verified,
            "browser_provider_verified": self.browser_provider_verified,
            "safety_policy_loaded": self.safety_policy_loaded,
            "human_approval_available": self.human_approval_available,
            "user_authenticated": self.user_authenticated,
            "sensitive_action_gate_enabled": self.sensitive_action_gate_enabled,
        }
        for name, passed in checks.items():
            if not passed:
                failing.append(name)
        return failing


class ExecutionModeConfig(BaseModel):
    mode: ExecutionMode = ExecutionMode.MOCK
    demo_mode: bool = False
    domain_allowlist: List[str] = Field(default_factory=list)
    blocked_actions: List[str] = Field(default_factory=list)


class LiveExecutionController:
    """Controls execution mode and enforces safety gates.

    LIVE mode requires explicit configuration.
    Never accidentally executes a real workflow from a unit test.
    """

    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.MOCK,
        domain_allowlist: Optional[DomainAllowlist] = None,
        demo_mode: bool = False,
    ) -> None:
        self._mode = mode
        self._domain_allowlist = domain_allowlist or DomainAllowlist()
        self._demo_mode = demo_mode
        self._safety_gate = LiveSafetyGate()
        self._execution_log: List[Dict[str, Any]] = []

    @property
    def mode(self) -> ExecutionMode:
        return self._mode

    @property
    def is_live(self) -> bool:
        return self._mode == ExecutionMode.LIVE

    @property
    def is_mock(self) -> bool:
        return self._mode == ExecutionMode.MOCK

    @property
    def demo_mode(self) -> bool:
        return self._demo_mode

    @property
    def safety_gate(self) -> LiveSafetyGate:
        return self._safety_gate

    @property
    def domain_allowlist(self) -> DomainAllowlist:
        return self._domain_allowlist

    def set_mode(self, mode: ExecutionMode) -> None:
        self._mode = mode
        self._log_event("mode_changed", {"new_mode": mode.value})

    def validate_live_execution(self) -> Dict[str, Any]:
        if self._mode != ExecutionMode.LIVE:
            return {
                "allowed": True,
                "reason": f"Mode is {self._mode.value}, not LIVE",
                "mode": self._mode.value,
            }

        if not self._safety_gate.all_passed():
            return {
                "allowed": False,
                "reason": "Live safety gate check failed",
                "failures": self._safety_gate.failures(),
                "mode": self._mode.value,
            }
        return {"allowed": True, "mode": self._mode.value}

    def check_domain(self, url: str) -> NavigationDecision:
        return self._domain_allowlist.check_navigation(url)

    def is_action_allowed(self, action_type: str) -> Dict[str, Any]:
        sensitive_actions = {
            "SUBMIT_APPLICATION", "SUBMIT_GRIEVANCE",
            "MAKE_PAYMENT", "UPDATE_RECORD", "DELETE_DATA",
        }
        if action_type in sensitive_actions and self._mode == ExecutionMode.LIVE:
            if not self._safety_gate.sensitive_action_gate_enabled:
                return {
                    "allowed": False,
                    "reason": f"Sensitive action '{action_type}' requires safety gate in LIVE mode",
                }
        return {"allowed": True}

    def record_approval(self, action_type: str, approval_id: str) -> None:
        self._log_event("approval_recorded", {
            "action_type": action_type,
            "approval_id": approval_id,
        })

    def configure_for_demo(self) -> None:
        self._demo_mode = True
        self._log_event("demo_configured", {})

    def _log_event(self, event_type: str, metadata: Dict[str, Any]) -> None:
        self._execution_log.append({
            "event_type": event_type,
            "metadata": metadata,
        })

    def get_execution_log(self) -> List[Dict[str, Any]]:
        return list(self._execution_log)

    def summary(self) -> Dict[str, Any]:
        return {
            "mode": self._mode.value,
            "demo_mode": self._demo_mode,
            "safety_gate_passed": self._safety_gate.all_passed(),
            "allowed_domains": len(self._domain_allowlist.get_allowed_domains()),
            "execution_events": len(self._execution_log),
        }
