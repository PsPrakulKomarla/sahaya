"""Structured error handling and correlation IDs.

Provides consistent error responses and request correlation.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorCode(str):
    """Standard error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    WORKFLOW_INVALID = "WORKFLOW_INVALID"
    BROWSER_ERROR = "BROWSER_ERROR"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


class ErrorDetail(BaseModel):
    """Structured error detail."""
    code: str
    message: str
    field: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: ErrorDetail
    request_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    path: Optional[str] = None


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to all requests and responses."""

    def __init__(self, app: FastAPI, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next):
        # Get or generate correlation ID
        correlation_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Add to response headers
        response = await call_next(request)
        response.headers[self.header_name] = correlation_id
        return response


def create_error_response(
    request: Request,
    code: str,
    message: str,
    status_code: int,
    field: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
) -> JSONResponse:
    """Create a standardized error response."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    error = ErrorDetail(
        code=code,
        message=message,
        field=field,
        context=context or {},
    )

    response = ErrorResponse(
        error=error,
        request_id=correlation_id,
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
        headers={f"X-Request-ID": correlation_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"]) if err["loc"] else None
        errors.append(
            ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR,
                message=err["msg"],
                field=field,
                context={"type": err["type"]},
            )
        )

    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR,
                message="Request validation failed",
                context={"errors": [e.model_dump() for e in errors]},
            ),
            request_id=correlation_id,
            path=str(request.url.path),
        ).model_dump(),
        headers={f"X-Request-ID": correlation_id},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with structured format."""
    return create_error_response(
        request=request,
        code=ErrorCode.AUTHORIZATION_FAILED if exc.status_code == 403 else ErrorCode.RESOURCE_NOT_FOUND,
        message=exc.detail if isinstance(exc.detail, str) else "Request failed",
        status_code=exc.status_code,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    # Log the full exception for debugging
    logger.exception(
        "unhandled_exception",
        request_id=correlation_id,
        path=str(request.url.path),
        error=str(exc),
    )

    # Return safe error to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred. Please try again later.",
            ),
            request_id=correlation_id,
            path=str(request.url.path),
        ).model_dump(),
        headers={f"X-Request-ID": correlation_id},
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Register all error handlers."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


# Re-export for convenience
__all__ = [
    "ErrorCode",
    "ErrorDetail",
    "ErrorResponse",
    "CorrelationIdMiddleware",
    "create_error_response",
    "setup_error_handlers",
    "validation_exception_handler",
    "http_exception_handler",
    "generic_exception_handler",
]