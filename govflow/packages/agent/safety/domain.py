"""DomainAllowlist — restricts browser navigation to approved domains.

Prevents accidental navigation to malicious or unrelated sites.
"""
from __future__ import annotations

from typing import List, Optional, Set
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class DomainEntry(BaseModel):
    domain: str
    description: str = ""
    requires_https: bool = True


class NavigationDecision(BaseModel):
    allowed: bool
    reason: str = ""
    domain: str = ""
    matched_entry: Optional[str] = None


class DomainAllowlist:
    """Restricts browser navigation to approved government domains.

    The browser must refuse navigation to unexpected domains
    unless explicitly allowed. This prevents accidental navigation
    to malicious or unrelated sites.
    """

    def __init__(self, allowed_domains: Optional[List[DomainEntry]] = None) -> None:
        self._entries: List[DomainEntry] = allowed_domains or []
        self._domain_set: Set[str] = {e.domain.lower() for e in self._entries}

    def add_domain(self, domain: str, description: str = "", requires_https: bool = True) -> None:
        entry = DomainEntry(domain=domain, description=description, requires_https=requires_https)
        self._entries.append(entry)
        self._domain_set.add(domain.lower())

    def remove_domain(self, domain: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.domain.lower() != domain.lower()]
        self._domain_set.discard(domain.lower())
        return len(self._entries) < before

    def is_allowed(self, url: str) -> bool:
        return self.check_navigation(url).allowed

    def check_navigation(self, url: str) -> NavigationDecision:
        try:
            parsed = urlparse(url)
        except Exception:
            return NavigationDecision(allowed=False, reason="Invalid URL")

        domain = parsed.hostname or ""
        if not domain:
            return NavigationDecision(allowed=False, reason="No domain in URL")

        domain_lower = domain.lower()
        if domain_lower in self._domain_set:
            entry = next((e for e in self._entries if e.domain.lower() == domain_lower), None)
            if entry and entry.requires_https and parsed.scheme != "https":
                return NavigationDecision(
                    allowed=False,
                    reason=f"Domain '{domain}' requires HTTPS but got '{parsed.scheme}'",
                    domain=domain,
                )
            return NavigationDecision(allowed=True, domain=domain, matched_entry=domain_lower)

        for entry in self._entries:
            if domain_lower.endswith("." + entry.domain.lower()):
                if entry.requires_https and parsed.scheme != "https":
                    return NavigationDecision(
                        allowed=False,
                        reason=f"Domain '{domain}' requires HTTPS",
                        domain=domain,
                    )
                return NavigationDecision(allowed=True, domain=domain, matched_entry=entry.domain)

        return NavigationDecision(
            allowed=False,
            reason=f"Domain '{domain}' is not in the allowlist",
            domain=domain,
        )

    def get_allowed_domains(self) -> List[str]:
        return [e.domain for e in self._entries]

    def list_entries(self) -> List[DomainEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._domain_set.clear()
