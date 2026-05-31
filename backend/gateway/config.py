from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gateway Service"
    app_version: str = "1.0.0"
    environment: Literal["dev", "development", "prod", "production"] = "development"
    debug: bool = True
    
    api_v1_prefix: str = "/api/v1"
    
    user_service_url: str = Field(default="http://localhost:8000")
    admin_service_url: str = Field(default="http://localhost:8003")
    event_service_url: str = Field(default="http://localhost:8002")
    media_service_url: str = Field(default="http://localhost:8006")
    notification_service_url: str = Field(default="http://localhost:8001")
    maps_service_url: str = Field(default="http://localhost:8004")
    
    http_timeout: float = 30.0
    
    jwt_secret: str = Field(
        default="super-secret-key-change-in-production-please-use-64-characters-minimum-please",
        validation_alias=AliasChoices("JWT_SECRET", "SECRET_KEY"),
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM"))
    
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
