"""Tests for application configuration defaults."""
from app.core.config import settings


def test_settings_defaults() -> None:
    assert settings.APP_NAME == "GovFlow AI"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.ENVIRONMENT == "test"
    assert isinstance(settings.DEBUG, bool)
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")
    assert settings.REDIS_URL.startswith("redis://")
    assert settings.CORS_ORIGINS == ["http://localhost:3000"]
    assert "en" in settings.OCR_LANGUAGES


def test_settings_reads_environment(monkeypatch) -> None:
    from app.core.config import Settings

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ci:ci@db:5432/govflow_test",
    )
    fresh = Settings()
    assert fresh.DATABASE_URL == "postgresql+asyncpg://ci:ci@db:5432/govflow_test"