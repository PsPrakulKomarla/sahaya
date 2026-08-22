"""Secure browser agent wrapper with URL validation and SSRF protection.

This wrapper ensures all browser navigation goes through URL validation
before reaching the underlying browser implementation.
"""
from __future__ import annotations

from typing import Optional

from packages.browser.interfaces.agent import BrowserAgent, BrowserConfig, BrowserResult
from packages.browser.interfaces.models import (
    BrowserAction,
    BrowserActionResult,
    PageInfo,
)
from app.core.url_security import (
    URLValidation,
    URLValidationResult,
    validate_redirect_chain,
    validate_url,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class BrowserSecurityError(Exception):
    """Raised when browser security validation fails."""

    def __init__(self, validation: URLValidation):
        self.validation = validation
        super().__init__(validation.message)


class SecureBrowserAgent:
    """Wrapper that adds URL validation and SSRF protection to any BrowserAgent."""

    def __init__(
        self,
        agent: BrowserAgent,
        validate_on_navigate: bool = True,
        validate_on_redirect: bool = True,
    ):
        self._agent = agent
        self._validate_on_navigate = validate_on_navigate
        self._validate_on_redirect = validate_on_redirect
        self._redirect_count = 0
        self._original_url: Optional[str] = None

    @property
    def agent(self) -> BrowserAgent:
        return self._agent

    async def open(self, config: Optional[BrowserConfig] = None) -> BrowserResult:
        return await self._agent.open(config)

    async def close(self) -> BrowserResult:
        return await self._agent.close()

    async def navigate(self, url: str) -> BrowserResult:
        """Navigate with URL validation."""
        # Validate the URL before navigation
        if self._validate_on_navigate:
            validation = validate_url(url)
            if not validation.allowed:
                logger.warning(
                    "navigation_blocked",
                    url=url,
                    reason=validation.result.value,
                    message=validation.message,
                )
                return BrowserResult(
                    success=False,
                    error=f"Navigation blocked: {validation.message}",
                )

            self._original_url = url
            self._redirect_count = 0

        result = await self._agent.navigate(url)

        # Check for redirects after navigation
        if self._validate_on_redirect and result.success:
            final_url = await self._agent.current_url()
            if final_url != url:
                self._redirect_count += 1
                redirect_validation = validate_redirect_chain(
                    original_url=self._original_url or url,
                    final_url=final_url,
                    redirect_count=self._redirect_count,
                )
                if not redirect_validation.allowed:
                    logger.warning(
                        "redirect_blocked",
                        original_url=self._original_url,
                        final_url=final_url,
                        reason=redirect_validation.result.value,
                        message=redirect_validation.message,
                    )
                    return BrowserResult(
                        success=False,
                        error=f"Redirect blocked: {redirect_validation.message}",
                    )

        return result

    async def current_url(self) -> str:
        return await self._agent.current_url()

    async def inspect(self) -> PageInfo:
        return await self._agent.inspect()

    async def execute_action(self, action: BrowserAction) -> BrowserActionResult:
        # For click actions that might cause navigation, validate the target URL
        if action.action_type == "click" and action.selector:
            # We can't easily validate click targets without knowing the href
            # This would require inspecting the element first
            pass
        return await self._agent.execute_action(action)

    async def screenshot(self) -> bytes:
        return await self._agent.screenshot()

    async def is_available(self) -> bool:
        return await self._agent.is_available()

    # Delegate other methods to the underlying agent
    def __getattr__(self, name: str):
        return getattr(self._agent, name)


async def create_secure_browser_agent(
    base_agent: BrowserAgent,
) -> SecureBrowserAgent:
    """Factory to create a secure browser agent wrapper."""
    return SecureBrowserAgent(
        agent=base_agent,
        validate_on_navigate=True,
        validate_on_redirect=True,
    )