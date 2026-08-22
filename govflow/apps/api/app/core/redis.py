"""Async Redis abstraction.

Provides a small, typed facade over ``redis.asyncio`` with JSON
serialization helpers. Services depend on ``RedisClient`` (via the
``get_redis`` dependency) instead of reaching for the raw client, keeping
the rest of the application decoupled from the underlying library.
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis as AsyncRedis

from app.core.config import settings


class RedisClient:
    """Thin async facade over a Redis connection pool."""

    def __init__(self, url: str, decode_responses: bool = True) -> None:
        self._url = url
        self._client: AsyncRedis[Any] = aioredis.from_url(
            url,
            decode_responses=decode_responses,
            health_check_interval=30,
        )

    @property
    def url(self) -> str:
        """The connection URL this client was created with."""
        return self._url

    async def ping(self) -> bool:
        """Return True when Redis responds to PING."""
        try:
            result = await self._client.ping()
            return bool(result)
        except Exception:
            return False

    async def set_json(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Serialize ``value`` to JSON and store it under ``key``.

        ``ttl`` is an optional expiry in seconds. Returns True on success.
        """
        payload = json.dumps(value)
        return bool(await self._client.set(key, payload, ex=ttl))

    async def get_json(self, key: str) -> Any | None:
        """Fetch and deserialize the JSON value stored under ``key``."""
        payload = await self._client.get(key)
        if payload is None:
            return None
        return json.loads(payload)

    async def delete(self, key: str) -> bool:
        """Delete ``key``. Returns True when at least one key was removed."""
        return bool(await self._client.delete(key))

    async def exists(self, key: str) -> bool:
        """Return True when ``key`` exists in Redis."""
        return bool(await self._client.exists(key))

    async def close(self) -> None:
        """Close the underlying connection pool."""
        await self._client.aclose()  # type: ignore[attr-defined]


_client: RedisClient | None = None


def get_redis() -> RedisClient:
    """Dependency provider returning the shared Redis client singleton."""
    global _client
    if _client is None:
        _client = RedisClient(settings.REDIS_URL)
    return _client


async def close_redis() -> None:
    """Close and reset the shared Redis client (used at shutdown)."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
