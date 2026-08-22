"""URL validation and security.

Provides domain allowlist, SSRF protection, and URL validation.
"""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class URLValidationResult(str, Enum):
    ALLOWED = "allowed"
    BLOCKED_DOMAIN = "blocked_domain"
    BLOCKED_PRIVATE_IP = "blocked_private_ip"
    BLOCKED_LOCALHOST = "blocked_localhost"
    BLOCKED_SCHEME = "blocked_scheme"
    BLOCKED_PORT = "blocked_port"
    INVALID_URL = "invalid_url"
    MAX_REDIRECTS_EXCEEDED = "max_redirects_exceeded"
    SUSPICIOUS_REDIRECT = "suspicious_redirect"


@dataclass
class URLValidation:
    """Result of URL validation."""
    allowed: bool
    result: URLValidationResult
    message: str
    final_url: Optional[str] = None
    redirect_count: int = 0


# Private IP ranges that should never be accessible
PRIVATE_IP_RANGES = [
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
    ipaddress.IPv4Network("127.0.0.0/8"),
    ipaddress.IPv4Network("169.254.0.0/16"),  # Link-local
    ipaddress.IPv6Network("::1/128"),  # IPv6 localhost
    ipaddress.IPv6Network("fc00::/7"),  # IPv6 unique local
    ipaddress.IPv6Network("fe80::/10"),  # IPv6 link-local
]

# Cloud metadata endpoints to block
CLOUD_METADATA_HOSTS = [
    "169.254.169.254",  # AWS, GCP, Azure, DigitalOcean
    "metadata.google.internal",  # GCP
    "metadata.azure.com",  # Azure
    "metadata.packet.net",  # Packet/Equinix
    "metadata.digitalocean.com",  # DigitalOcean
]

# Allowed schemes
ALLOWED_SCHEMES = {"https"}

# Blocked ports (common internal services)
BLOCKED_PORTS = {
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    110,   # POP3
    143,   # IMAP
    445,   # SMB
    993,   # IMAPS
    995,   # POP3S
    1433,  # MSSQL
    1521,  # Oracle
    3306,  # MySQL
    3389,  # RDP
    5432,  # PostgreSQL
    5900,  # VNC
    6379,  # Redis
    8080,  # HTTP Alt
    8443,  # HTTPS Alt
    9200,  # Elasticsearch
    27017, # MongoDB
}


def is_private_ip(hostname: str) -> bool:
    """Check if hostname resolves to a private IP address."""
    try:
        # Try parsing as IP directly
        ip = ipaddress.ip_address(hostname)
        return any(ip in network for network in PRIVATE_IP_RANGES)
    except ValueError:
        # Not an IP address, would need DNS resolution
        # For now, check if it's a known metadata host
        return hostname.lower() in CLOUD_METADATA_HOSTS


def is_blocked_port(port: Optional[int]) -> bool:
    """Check if port is blocked."""
    if port is None:
        return False
    return port in BLOCKED_PORTS


def normalize_domain(domain: str) -> str:
    """Normalize domain for comparison."""
    return domain.lower().strip().rstrip(".")


def is_domain_allowed(url: str) -> tuple[bool, str]:
    """Check if domain is in allowlist."""
    if not settings.ALLOWED_DOMAINS:
        return True, "No domain allowlist configured (development mode)"

    try:
        parsed = urlparse(url)
        domain = normalize_domain(parsed.netloc.split(":")[0])

        # Check blocked domains first
        for blocked in settings.BLOCKED_DOMAINS:
            if domain == normalize_domain(blocked) or domain.endswith("." + normalize_domain(blocked)):
                return False, f"Domain '{domain}' is blocked"

        # Check allowed domains
        for allowed in settings.ALLOWED_DOMAINS:
            allowed_norm = normalize_domain(allowed)
            if domain == allowed_norm or domain.endswith("." + allowed_norm):
                return True, f"Domain '{domain}' is allowed"

        return False, f"Domain '{domain}' not in allowlist"

    except Exception as e:
        logger.error("domain_check_failed", url=url, error=str(e))
        return False, f"Domain validation failed: {e}"


def validate_url(url: str, follow_redirects: bool = False) -> URLValidation:
    """Validate a URL for security.

    Args:
        url: The URL to validate
        follow_redirects: Whether to follow and validate redirects (not implemented here)

    Returns:
        URLValidation result
    """
    # Basic URL parsing
    try:
        parsed = urlparse(url)
    except Exception as e:
        return URLValidation(
            allowed=False,
            result=URLValidationResult.INVALID_URL,
            message=f"Invalid URL: {e}",
        )

    # Check scheme
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return URLValidation(
            allowed=False,
            result=URLValidationResult.BLOCKED_SCHEME,
            message=f"Scheme '{parsed.scheme}' not allowed. Only HTTPS permitted.",
        )

    # Check hostname
    hostname = parsed.hostname
    if not hostname:
        return URLValidation(
            allowed=False,
            result=URLValidationResult.INVALID_URL,
            message="No hostname in URL",
        )

    # Check for localhost
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        if not settings.DEBUG:
            return URLValidation(
                allowed=False,
                result=URLValidationResult.BLOCKED_LOCALHOST,
                message="Localhost access blocked in production",
            )
        logger.warning("localhost_access_allowed_in_debug", url=url)

    # Check for private IPs
    if is_private_ip(hostname):
        if not settings.BROWSER_ALLOW_PRIVATE_IPS:
            return URLValidation(
                allowed=False,
                result=URLValidationResult.BLOCKED_PRIVATE_IP,
                message=f"Access to private IP '{hostname}' blocked",
            )
        logger.warning("private_ip_access_allowed", url=url, host=hostname)

    # Check port
    if is_blocked_port(parsed.port):
        return URLValidation(
            allowed=False,
            result=URLValidationResult.BLOCKED_PORT,
            message=f"Port {parsed.port} is blocked",
        )

    # Check domain allowlist
    allowed, message = is_domain_allowed(url)
    if not allowed:
        return URLValidation(
            allowed=False,
            result=URLValidationResult.BLOCKED_DOMAIN,
            message=message,
        )

    return URLValidation(
        allowed=True,
        result=URLValidationResult.ALLOWED,
        message="URL validation passed",
        final_url=url,
    )


def validate_redirect_chain(
    original_url: str,
    final_url: str,
    redirect_count: int,
) -> URLValidation:
    """Validate a redirect chain.

    Args:
        original_url: The originally requested URL
        final_url: The final URL after redirects
        redirect_count: Number of redirects followed
    """
    if redirect_count > settings.BROWSER_MAX_REDIRECTS:
        return URLValidation(
            allowed=False,
            result=URLValidationResult.MAX_REDIRECTS_EXCEEDED,
            message=f"Too many redirects ({redirect_count} > {settings.BROWSER_MAX_REDIRECTS})",
            redirect_count=redirect_count,
        )

    # Validate final URL
    validation = validate_url(final_url)
    validation.redirect_count = redirect_count

    # Check if redirect went to a different domain (potential open redirect)
    original_domain = urlparse(original_url).netloc
    final_domain = urlparse(final_url).netloc

    if original_domain != final_domain:
        # Allow if both are in allowlist
        orig_allowed, _ = is_domain_allowed(original_url)
        final_allowed, _ = is_domain_allowed(final_url)

        if not (orig_allowed and final_allowed):
            return URLValidation(
                allowed=False,
                result=URLValidationResult.SUSPICIOUS_REDIRECT,
                message=f"Suspicious cross-domain redirect: {original_domain} -> {final_domain}",
                final_url=final_url,
                redirect_count=redirect_count,
            )

    return validation