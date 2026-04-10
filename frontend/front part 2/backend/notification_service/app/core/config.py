"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Project
    PROJECT_NAME: str = "Notification Service Плечом к плечу"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production-please-use-64-characters-minimum-!!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shoulder_to_shoulder_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # NATS
    NATS_URL: str = "nats://localhost:4222"

    # Service communications
    USER_SERVICE_URL: str = "http://localhost:8000"
    GATEWAY_URL: str = "http://localhost:8000"

    # Scheduler
    SCHEDULER_INTERVAL_SECONDS: int = 10  # Check pending notifications every 10 seconds

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        """Config settings."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
