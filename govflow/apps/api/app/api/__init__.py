from app.api.health import router as health_router
from app.api.services import router as services_router
from app.api.documents import router as documents_router
from app.api.applications import router as applications_router
from app.api.tracking import router as tracking_router

__all__ = [
    "health_router",
    "services_router",
    "documents_router",
    "applications_router",
    "tracking_router",
]
