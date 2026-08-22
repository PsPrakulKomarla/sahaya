"""GovFlow AI - Main Application Entry Point.

This module configures the FastAPI application with all middleware,
routers, error handlers, and lifecycle management.
"""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.services import router as services_router
from app.api.documents import router as documents_router
from app.api.applications import router as applications_router
from app.api.tracking import router as tracking_router
from app.api.workflows import router as workflows_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.errors import CorrelationIdMiddleware, setup_error_handlers
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import RateLimitMiddleware
from app.core.redis import close_redis

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting", version=settings.APP_VERSION)
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as exc:
        logger.error("database_initialization_failed", error=str(exc))
    yield
    logger.info("application_shutting_down")
    await close_db()
    await close_redis()
    logger.info("database_closed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GovFlow AI - Universal Government Service Browser Agent API",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Correlation ID middleware (must be first to capture all requests)
app.add_middleware(CorrelationIdMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)

# Setup structured error handlers
setup_error_handlers(app)

# Include routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router)  # Also at root for probes
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(services_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(applications_router, prefix=settings.API_V1_PREFIX)
app.include_router(tracking_router, prefix=settings.API_V1_PREFIX)
app.include_router(workflows_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }