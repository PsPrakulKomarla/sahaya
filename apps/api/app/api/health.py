from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", tags=["health"])
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/detailed", tags=["health"])
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> dict:
    services = {}
    overall_status = "healthy"

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        services["database"] = {"status": "healthy"}
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        services["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "unhealthy"

    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        services["redis"] = {"status": "healthy"}
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        services["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded" if overall_status == "healthy" else overall_status

    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": services,
    }


@router.get("/health/ready", tags=["health"])
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        return {"status": "ready"}
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return {"status": "not_ready", "error": str(e)}


@router.get("/health/live", tags=["health"])
async def liveness_check() -> dict:
    return {"status": "alive"}