"""Rate limiting middleware using Redis.

Provides configurable rate limiting per endpoint or globally.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.redis import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed rate limiting middleware.

    Uses sliding window algorithm with Redis sorted sets.
    """

    def __init__(
        self,
        app,
        requests: int = 100,
        window_seconds: int = 60,
        exempt_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        self.exempt_paths = exempt_paths or ["/health", "/health/", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Skip if rate limiting is disabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Get client identifier (IP + user if authenticated)
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, "user_id", None)
        key = f"ratelimit:{user_id or client_ip}"

        redis_client = get_redis()
        now = time.time()
        window_start = now - self.window_seconds

        try:
            # Use Redis sorted set for sliding window
            pipe = redis_client._client.pipeline()
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current requests
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Set expiry
            pipe.expire(key, self.window_seconds + 1)
            results = await pipe.execute()

            current_count = results[1]

            if current_count >= self.requests:
                # Rate limited
                retry_after = int(self.window_seconds - (now - window_start))
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {self.requests} per {self.window_seconds}s",
                        "retry_after": retry_after,
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(now + self.window_seconds)),
                        "Retry-After": str(retry_after),
                    },
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests)
            response.headers["X-RateLimit-Remaining"] = str(self.requests - current_count - 1)
            response.headers["X-RateLimit-Reset"] = str(int(now + self.window_seconds))
            return response

        except Exception:
            # If Redis is unavailable, allow request (fail open)
            # Log the error in production
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"


def create_rate_limiter(
    requests: int,
    window_seconds: int,
    exempt_paths: Optional[list[str]] = None,
) -> type[RateLimitMiddleware]:
    """Factory to create a rate limiter middleware class with custom settings."""
    class CustomRateLimiter(RateLimitMiddleware):
        def __init__(self, app):
            super().__init__(app, requests, window_seconds, exempt_paths)

    return CustomRateLimiter