import pytest
from unittest.mock import AsyncMock
from packages.agent.safety.domain import DomainAllowlist, DomainEntry, NavigationDecision
from packages.agent.executor.live_mode import (
    LiveExecutionController, ExecutionMode, LiveSafetyGate,
)


@pytest.fixture
def gov_domain_allowlist():
    al = DomainAllowlist()
    al.add_domain("karnataka.gov.in", description="Karnataka State Portal")
    al.add_domain("serviceonline.gov.in", description="Service Online Portal")
    al.add_domain("uidai.gov.in", description="UIDAI Portal")
    return al


class TestDomainAllowlist:
    def test_allowed_domain_navigation(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("https://karnataka.gov.in")
        assert result.allowed is True
        assert result.domain == "karnataka.gov.in"

    def test_subdomain_of_allowed_domain(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("https://sub.karnataka.gov.in")
        assert result.allowed is True
        assert result.matched_entry == "karnataka.gov.in"

    def test_unknown_domain_blocked(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("https://malicious-site.com")
        assert result.allowed is False
        assert "not in the allowlist" in result.reason

    def test_https_required_http_blocked(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("http://karnataka.gov.in")
        assert result.allowed is False
        assert "requires HTTPS" in result.reason

    def test_https_required_https_allowed(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("https://karnataka.gov.in/page")
        assert result.allowed is True

    def test_empty_domain_blocked(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("")
        assert result.allowed is False

    def test_invalid_url_blocked(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("://not-a-url")
        assert result.allowed is False
        # URL has no domain, so it's blocked
        assert "No domain" in result.reason or "not in the allowlist" in result.reason

    def test_add_and_remove_domain(self, gov_domain_allowlist):
        gov_domain_allowlist.add_domain("example.gov.in", requires_https=False)
        assert gov_domain_allowlist.is_allowed("http://example.gov.in") is True
        removed = gov_domain_allowlist.remove_domain("example.gov.in")
        assert removed is True
        assert gov_domain_allowlist.is_allowed("https://example.gov.in") is False

    def test_clear_all_domains(self, gov_domain_allowlist):
        assert len(gov_domain_allowlist.get_allowed_domains()) == 3
        gov_domain_allowlist.clear()
        assert len(gov_domain_allowlist.get_allowed_domains()) == 0
        assert gov_domain_allowlist.is_allowed("https://karnataka.gov.in") is False

    def test_list_entries(self, gov_domain_allowlist):
        entries = gov_domain_allowlist.list_entries()
        assert len(entries) == 3
        domains = {e.domain for e in entries}
        assert domains == {"karnataka.gov.in", "serviceonline.gov.in", "uidai.gov.in"}


class TestLiveExecutionController:
    def test_mock_mode_allows_execution(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.MOCK)
        result = ctrl.validate_live_execution()
        assert result["allowed"] is True
        assert result["mode"] == "MOCK"

    def test_live_mode_without_safety_gate_blocked(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)
        result = ctrl.validate_live_execution()
        assert result["allowed"] is False
        assert "failures" in result

    def test_live_mode_with_all_safety_gates_passed(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)
        ctrl._safety_gate = LiveSafetyGate(
            service_verified=True,
            domain_verified=True,
            workflow_version_verified=True,
            browser_provider_verified=True,
            safety_policy_loaded=True,
            human_approval_available=True,
            user_authenticated=True,
            sensitive_action_gate_enabled=True,
        )
        result = ctrl.validate_live_execution()
        assert result["allowed"] is True

    def test_live_mode_domain_check_uses_allowlist(self, gov_domain_allowlist):
        ctrl = LiveExecutionController(
            mode=ExecutionMode.LIVE,
            domain_allowlist=gov_domain_allowlist,
        )
        allowed = ctrl.check_domain("https://karnataka.gov.in")
        blocked = ctrl.check_domain("https://unknown.com")
        assert allowed.allowed is True
        assert blocked.allowed is False

    def test_sensitive_action_without_gate_blocked(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)
        ctrl._safety_gate.sensitive_action_gate_enabled = False
        result = ctrl.is_action_allowed("SUBMIT_APPLICATION")
        assert result["allowed"] is False
        assert "safety gate" in result["reason"]

    def test_demo_mode_configuration(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.MOCK, demo_mode=True)
        assert ctrl.demo_mode is True
        ctrl.configure_for_demo()
        assert ctrl.demo_mode is True
        log = ctrl.get_execution_log()
        assert any(e["event_type"] == "demo_configured" for e in log)

    def test_mode_switching_logs_events(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.MOCK)
        ctrl.set_mode(ExecutionMode.LIVE)
        ctrl.set_mode(ExecutionMode.TEST)
        log = ctrl.get_execution_log()
        assert len(log) == 2
        assert log[0]["metadata"]["new_mode"] == "LIVE"
        assert log[1]["metadata"]["new_mode"] == "TEST"


class TestSecurityScenarios:
    def test_unauthorized_domain_navigation_attempt(self, gov_domain_allowlist):
        result = gov_domain_allowlist.check_navigation("https://phishing-gov.in")
        assert result.allowed is False

    def test_arbitrary_url_navigation_blocked(self, gov_domain_allowlist):
        urls = [
            "https://evil.com/steal",
            "http://karnataka.gov.in/phish",
            "ftp://karnataka.gov.in",
        ]
        for url in urls:
            assert gov_domain_allowlist.is_allowed(url) is False

    def test_sensitive_action_without_approval(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)
        actions = [
            "SUBMIT_APPLICATION",
            "SUBMIT_GRIEVANCE",
            "MAKE_PAYMENT",
            "UPDATE_RECORD",
            "DELETE_DATA",
        ]
        for action in actions:
            result = ctrl.is_action_allowed(action)
            assert result["allowed"] is False

    def test_session_expiration_detection(self):
        ctrl = LiveExecutionController(mode=ExecutionMode.LIVE)
        ctrl._safety_gate.user_authenticated = False
        result = ctrl.validate_live_execution()
        assert result["allowed"] is False
        assert "user_authenticated" in result["failures"]

    def test_domain_allowlist_with_multiple_government_portals(self, gov_domain_allowlist):
        portals = {
            "https://karnataka.gov.in": True,
            "https://serviceonline.gov.in": True,
            "https://uidai.gov.in": True,
            "https://sub.serviceonline.gov.in": True,
            "https://fake-gov.in": False,
            "http://karnataka.gov.in": False,
        }
        for url, expected in portals.items():
            assert gov_domain_allowlist.is_allowed(url) == expected
