from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging import configure_logging, get_logger
from app.api.health import router as health_router
from app.api.services import router as services_router
from app.api.intent import router as intent_router
from app.api.agent import router as agent_router
from packages.services import register_default_services

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting", version=settings.APP_VERSION)

    register_default_services()
    logger.info("services_registered")

    await init_db()
    logger.info("database_initialized")

    yield

    logger.info("application_shutting_down")
    await close_db()
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
app.include_router(services_router, prefix=settings.API_V1_PREFIX)
app.include_router(intent_router, prefix=settings.API_V1_PREFIX)
app.include_router(agent_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "services": f"{settings.API_V1_PREFIX}/services",
        "intent": f"{settings.API_V1_PREFIX}/intent",
        "agent": f"{settings.API_V1_PREFIX}/agent",
    }