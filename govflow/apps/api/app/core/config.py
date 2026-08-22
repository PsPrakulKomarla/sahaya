from functools import lru_cache

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

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    OCR_LANGUAGES: list[str] = ["en", "kn", "hi"]
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()