from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Event Service"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shoulder_to_shoulder_events"
    NATS_URL: str = "nats://localhost:4222"
    SECRET_KEY: str

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.is_production:
            weak_values = {
                "super-secret-key-change-in-production-please-use-64-characters-minimum-please",
                "CHANGE_ME_GENERATE_64_RANDOM_CHARS",
            }
            if self.SECRET_KEY in weak_values or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be changed to a strong random value in production")
        return self

settings = Settings()
