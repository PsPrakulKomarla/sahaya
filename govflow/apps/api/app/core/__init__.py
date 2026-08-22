from app.core.auth import (
    get_current_user,
    get_current_user_optional,
    require_role,
    verify_resource_ownership,
)
from app.core.config import get_settings, settings
from app.core.database import Base, async_session_maker, close_db, engine, get_db, init_db
from app.core.errors import (
    CorrelationIdMiddleware,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    create_error_response,
    setup_error_handlers,
)
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import RateLimitMiddleware
from app.core.redis import RedisClient, close_redis, get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.url_security import (
    URLValidation,
    URLValidationResult,
    is_domain_allowed,
    is_private_ip,
    validate_redirect_chain,
    validate_url,
)

__all__ = [
    "settings",
    "get_settings",
    "engine",
    "async_session_maker",
    "Base",
    "get_db",
    "init_db",
    "close_db",
    "RedisClient",
    "get_redis",
    "close_redis",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "configure_logging",
    "get_logger",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "verify_resource_ownership",
    "RateLimitMiddleware",
    "CorrelationIdMiddleware",
    "ErrorCode",
    "ErrorDetail",
    "ErrorResponse",
    "create_error_response",
    "setup_error_handlers",
    "URLValidation",
    "URLValidationResult",
    "is_domain_allowed",
    "is_private_ip",
    "validate_redirect_chain",
    "validate_url",
]