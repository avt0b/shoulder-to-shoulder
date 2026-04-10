from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    environment: Literal["dev", "prod"] = "dev"
    debug: bool = True
    project_name: str = "Maps Microservice"
    version: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )


class DatabaseConfig(BaseSettings):
    postgres_url: str = Field(..., description="PostgreSQL connection URL")
    postgres_user: str = Field(...)
    postgres_password: str = Field(...)
    postgres_host: str = Field(...)
    postgres_db: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )


class CORSConfig(BaseSettings):
    allowed_origins: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_prefix="CORS_",
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

class Settings(BaseSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()