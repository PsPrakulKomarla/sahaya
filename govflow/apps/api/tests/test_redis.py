"""Tests for the Redis abstraction layer."""
import json
from typing import Tuple
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.redis import RedisClient


@pytest.fixture
def stub() -> Tuple[RedisClient, MagicMock]:
    """A RedisClient whose transport is stubbed with a MagicMock."""
    client = RedisClient(url="redis://localhost:6379/0")
    backend: MagicMock = MagicMock()
    client._client = backend  # type: ignore[misc]
    backend.aclose = AsyncMock()
    return client, backend


@pytest.mark.asyncio
async def test_ping_healthy(stub: Tuple[RedisClient, MagicMock]) -> None:
    client, backend = stub
    backend.ping = AsyncMock(return_value=True)
    assert await client.ping() is True
    backend.ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_ping_unreachable(stub: Tuple[RedisClient, MagicMock]) -> None:
    client, backend = stub
    backend.ping = AsyncMock(side_effect=ConnectionError("down"))
    assert await client.ping() is False


@pytest.mark.asyncio
async def test_json_roundtrip(stub: Tuple[RedisClient, MagicMock]) -> None:
    client, backend = stub
    payload = {"items": [1, 2], "ok": True}
    backend.set = AsyncMock(return_value=True)
    backend.get = AsyncMock(return_value=json.dumps(payload))

    assert await client.set_json("test:key", payload, ttl=60) is True
    backend.set.assert_awaited_once_with("test:key", json.dumps(payload), ex=60)
    assert await client.get_json("test:key") == payload


@pytest.mark.asyncio
async def test_get_json_missing(stub: Tuple[RedisClient, MagicMock]) -> None:
    client, backend = stub
    backend.get = AsyncMock(return_value=None)
    assert await client.get_json("missing:key") is None


@pytest.mark.asyncio
async def test_delete_and_exists(stub: Tuple[RedisClient, MagicMock]) -> None:
    client, backend = stub
    backend.delete = AsyncMock(return_value=1)
    backend.exists = AsyncMock(return_value=1)
    assert await client.delete("some:key") is True
    backend.delete.assert_awaited_once_with("some:key")
    assert await client.exists("some:key") is True


@pytest.mark.asyncio
async def test_close(stub: Tuple[RedisClient, MagicMock]) -> None:
    client, backend = stub
    await client.close()
    backend.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_redis_returns_singleton() -> None:
    from app.core import redis as redis_module

    await redis_module.close_redis()
    first = redis_module.get_redis()
    second = redis_module.get_redis()
    try:
        assert first is second
        assert first.url == "redis://localhost:6379/0"
    finally:
        await redis_module.close_redis()