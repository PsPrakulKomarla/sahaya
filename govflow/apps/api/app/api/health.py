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

    # Browser health check
    browser_status = "healthy"
    start = time.perf_counter()
    try:
        # Check if Playwright is available
        from playwright.async_api import async_playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        await browser.close()
        await playwright.stop()
        services["browser"] = {
            "status": "healthy",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception as exc:
        browser_status = "unhealthy"
        logger.error("browser_health_check_failed", error=str(exc))
        services["browser"] = {"status": "unhealthy", "error": str(exc)}

    # AI health check
    ai_status = "healthy"
    start = time.perf_counter()
    try:
        # Check if AI provider is configured
        if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            # Could add actual API call here
            services["ai"] = {
                "status": "configured",
                "provider": "openai",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        elif settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            services["ai"] = {
                "status": "configured",
                "provider": "anthropic",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        else:
            ai_status = "degraded"
            services["ai"] = {
                "status": "not_configured",
                "provider": settings.AI_PROVIDER,
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }
    except Exception as exc:
        ai_status = "unhealthy"
        logger.error("ai_health_check_failed", error=str(exc))
        services["ai"] = {"status": "unhealthy", "error": str(exc)}

    # Storage health check
    storage_status = "healthy"
    start = time.perf_counter()
    try:
        # Check if S3 is configured
        if settings.S3_ENDPOINT and settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            # Could add actual S3 connectivity check here
            services["storage"] = {
                "status": "configured",
                "endpoint": settings.S3_ENDPOINT,
                "bucket": settings.S3_BUCKET,
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        else:
            storage_status = "degraded"
            services["storage"] = {
                "status": "not_configured",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }
    except Exception as exc:
        storage_status = "unhealthy"
        logger.error("storage_health_check_failed", error=str(exc))
        services["storage"] = {"status": "unhealthy", "error": str(exc)}

    # Determine overall status
    statuses = [database_status, redis_status, browser_status, ai_status, storage_status]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif "unhealthy" in statuses:
        overall = "unhealthy"
    else:
        overall = "degraded"

    return {"status": overall, "services": services, **_service_info()}


@router.get("/health/browser")
async def browser_health_check() -> Dict[str, Any]:
    """Browser-specific health check."""
    start = time.perf_counter()
    try:
        from playwright.async_api import async_playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("about:blank")
        await browser.close()
        await playwright.stop()
        return {
            "status": "healthy",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            **_service_info(),
        }
    except Exception as exc:
        logger.error("browser_health_check_failed", error=str(exc))
        return {
            "status": "unhealthy",
            "error": str(exc),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            **_service_info(),
        }


@router.get("/health/ai")
async def ai_health_check() -> Dict[str, Any]:
    """AI provider health check."""
    start = time.perf_counter()
    try:
        provider = settings.AI_PROVIDER
        configured = False
        if provider == "openai" and settings.OPENAI_API_KEY:
            configured = True
        elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            configured = True
        elif provider == "local" and settings.LOCAL_MODEL_PATH:
            configured = True

        return {
            "status": "healthy" if configured else "not_configured",
            "provider": provider,
            "configured": configured,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            **_service_info(),
        }
    except Exception as exc:
        logger.error("ai_health_check_failed", error=str(exc))
        return {
            "status": "unhealthy",
            "error": str(exc),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            **_service_info(),
        }


@router.get("/health/storage")
async def storage_health_check() -> Dict[str, Any]:
    """Storage backend health check."""
    start = time.perf_counter()
    try:
        if settings.S3_ENDPOINT and settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            return {
                "status": "configured",
                "endpoint": settings.S3_ENDPOINT,
                "bucket": settings.S3_BUCKET,
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                **_service_info(),
            }
        else:
            return {
                "status": "not_configured",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                **_service_info(),
            }
    except Exception as exc:
        logger.error("storage_health_check_failed", error=str(exc))
        return {
            "status": "unhealthy",
            "error": str(exc),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            **_service_info(),
        }
