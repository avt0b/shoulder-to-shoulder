from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: Literal["development", "production"] = "development"
    PROJECT_NAME: str = "Admin Service — Плечом к плечу"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    NATS_URL: str = "nats://localhost:4222"

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
