from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging import configure_logging, get_logger
from app.core.redis import close_redis

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("application_starting", version=settings.APP_VERSION)
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as exc:
        # The API must still start (and report health) when PostgreSQL is
        # unavailable; alembic remains the schema source of truth.
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }