"""Operational health check endpoints.

The router is mounted both at the root (``/health``) and under the API
version prefix (``/api/v1/health``) so probes can use either path.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.redis import RedisClient, get_redis

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


def _service_info() -> Dict[str, Any]:
    """Base payload shared across health endpoints."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health: the process is up and carries service metadata."""
    return {"status": "healthy", **_service_info()}


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness probe — no external dependencies are touched."""
    return {"status": "alive", **_service_info()}


@router.get("/health/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis_client: RedisClient = Depends(get_redis),
) -> Dict[str, Any]:
    """Readiness probe: verifies PostgreSQL and Redis are reachable."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("database_readiness_failed", error=str(exc))
        return {"status": "not_ready", "error": str(exc)}

    try:
        available = await redis_client.ping()
    except Exception as exc:
        logger.error("redis_readiness_failed", error=str(exc))
        return {"status": "not_ready", "error": str(exc)}

    if not available:
        return {"status": "not_ready", "error": "redis unreachable"}
    return {"status": "ready", **_service_info()}


@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: RedisClient = Depends(get_redis),
) -> Dict[str, Any]:
    """Per-dependency health report with latency measurements."""
    services: Dict[str, Any] = {}

    database_status = "healthy"
    start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        services["database"] = {
            "status": "healthy",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception as exc:
        database_status = "unhealthy"
        logger.error("database_health_check_failed", error=str(exc))
        services["database"] = {"status": "unhealthy", "error": str(exc)}

    redis_status = "healthy"
    start = time.perf_counter()
    try:
        available = await redis_client.ping()
    except Exception as exc:
        redis_status = "unhealthy"
        logger.error("redis_health_check_failed", error=str(exc))
        services["redis"] = {"status": "unhealthy", "error": str(exc)}
    else:
        if not available:
            redis_status = "unhealthy"
        services["redis"] = {
            "status": "healthy" if available else "unhealthy",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }

    if database_status == "healthy" and redis_status == "healthy":
        overall = "healthy"
    elif database_status == "unhealthy":
        overall = "unhealthy"
    else:
        overall = "degraded"

    return {"status": overall, "services": services, **_service_info()}
