"""Application configuration with validation.

All security-sensitive settings MUST be provided via environment variables.
No defaults for secrets in production environments.
"""
import os
import warnings
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "GovFlow AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/govflow"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    REDIS_URL: str = "redis://localhost:6379/0"

    # SECURITY: No default for SECRET_KEY - must be set via env var in production
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    OCR_LANGUAGES: List[str] = ["en", "kn", "hi"]
    OCR_CONFIDENCE_THRESHOLD: float = 0.8

    PLAYWRIGHT_BROWSER: str = "chromium"
    PLAYWRIGHT_HEADLESS: bool = True
    WEBCMD_DAEMON_URL: str = "http://localhost:9222"

    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LOCAL_MODEL_PATH: str = ""

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "govflow-documents"
    S3_REGION: str = "us-east-1"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # URL security - domain allowlist
    ALLOWED_DOMAINS: List[str] = []
    BLOCKED_DOMAINS: List[str] = []

    # Browser security
    BROWSER_ALLOW_PRIVATE_IPS: bool = False
    BROWSER_MAX_REDIRECTS: int = 5

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: Optional[str]) -> str:
        """Ensure SECRET_KEY is set in production."""
        if v is None or v == "":
            env = os.getenv("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError(
                    "SECRET_KEY must be set via environment variable in production"
                )
            # Development: generate a warning but allow a generated key
            warnings.warn(
                "SECRET_KEY not set - using generated key. "
                "Set SECRET_KEY environment variable for production.",
                RuntimeWarning,
                stacklevel=2,
            )
            import secrets
            return secrets.token_urlsafe(32)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Warn about overly permissive CORS in production."""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production" and ("*" in v or len(v) == 0):
            warnings.warn(
                "CORS_ORIGINS is overly permissive for production. "
                "Explicitly list allowed origins.",
                RuntimeWarning,
                stacklevel=2,
            )
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate production-specific settings."""
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                warnings.warn(
                    "DEBUG=True in production - this exposes sensitive information.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            if not self.ALLOWED_DOMAINS:
                warnings.warn(
                    "ALLOWED_DOMAINS is empty - browser will not be able to navigate to any domain. "
                    "Configure allowed government portal domains.",
                    RuntimeWarning,
                    stacklevel=2,
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()