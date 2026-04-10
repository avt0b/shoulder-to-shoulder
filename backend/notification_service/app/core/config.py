"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    PROJECT_NAME: str = "Notification Service Плечом к плечу"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    NATS_URL: str = "nats://localhost:4222"

    LOG_LEVEL: str = "INFO"



settings = Settings()
