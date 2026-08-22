"""Tests for the health endpoints."""
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.redis import RedisClient, get_redis
from app.main import app

client = TestClient(app)


def _healthy_db() -> Any:
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock())
    return db


def _healthy_redis() -> RedisClient:
    redis_client = AsyncMock(spec=RedisClient)
    redis_client.ping.return_value = True
    return redis_client


@pytest.fixture
def healthy_dependencies() -> Any:
    async def override_db() -> Any:
        yield _healthy_db()

    async def override_redis() -> RedisClient:
        return _healthy_redis()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    yield
    app.dependency_overrides.clear()


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "GovFlow AI"
    assert "version" in body
    assert body["docs"] == "/docs"


@pytest.mark.parametrize("path", ["/health", "/api/v1/health"])
def test_health_check(path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "GovFlow AI"
    assert "timestamp" in body


@pytest.mark.parametrize("path", ["/health/live", "/api/v1/health/live"])
def test_liveness_check(path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_detailed_health_all_healthy(healthy_dependencies: Any) -> None:
    response = client.get("/health/detailed")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["services"]["database"]["status"] == "healthy"
    assert body["services"]["redis"]["status"] == "healthy"


def test_detailed_health_db_down() -> None:
    async def override_db() -> Any:
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=RuntimeError("db down"))
        yield db

    async def override_redis() -> RedisClient:
        return _healthy_redis()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    try:
        response = client.get("/health/detailed")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "unhealthy"
        assert body["services"]["database"]["status"] == "unhealthy"
        assert "error" in body["services"]["database"]
    finally:
        app.dependency_overrides.clear()


def test_detailed_health_redis_down() -> None:
    async def override_db() -> Any:
        yield _healthy_db()

    async def override_redis() -> RedisClient:
        redis_client = AsyncMock(spec=RedisClient)
        redis_client.ping.return_value = False
        return redis_client

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    try:
        response = client.get("/health/detailed")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "degraded"
        assert body["services"]["redis"]["status"] == "unhealthy"
    finally:
        app.dependency_overrides.clear()


def test_readiness_ready(healthy_dependencies: Any) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readiness_not_ready_db_down() -> None:
    async def override_db() -> Any:
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=RuntimeError("db down"))
        yield db

    async def override_redis() -> RedisClient:
        return _healthy_redis()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    try:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
    finally:
        app.dependency_overrides.clear()


def test_readiness_not_ready_redis_down(healthy_dependencies: Any) -> None:
    async def override_redis() -> RedisClient:
        redis_client = AsyncMock(spec=RedisClient)
        redis_client.ping.return_value = False
        return redis_client

    app.dependency_overrides[get_redis] = override_redis
    try:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
    finally:
        app.dependency_overrides.clear()