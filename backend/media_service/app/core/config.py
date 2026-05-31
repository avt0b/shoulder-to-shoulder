from pathlib import Path
from typing import List, Set

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        json_schema_extra={"populate_by_name": True},
    )

    # App
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Media Service"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/media_service"

    NATS_URL: str = "nats://localhost:4222"

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "dev-media"
    AWS_S3_REGION: str = "eu-central-1"
    AWS_S3_ENDPOINT_URL: str | None = "http://minio:9000"
    AWS_PUBLIC_URL: str = "http://localhost:8006"

    MAX_FILE_SIZE: int = 10_485_760  # 10 MB
    ALLOWED_CONTENT_TYPES_STR: str = "image/jpeg,image/png,application/pdf"
    ALLOWED_PURPOSES_STR: str = "avatar,event,spot,badge"

    @property
    def ALLOWED_CONTENT_TYPES(self) -> List[str]:
        return [item.strip() for item in self.ALLOWED_CONTENT_TYPES_STR.split(",") if item.strip()]

    @property
    def ALLOWED_PURPOSES(self) -> Set[str]:
        return {item.strip() for item in self.ALLOWED_PURPOSES_STR.split(",") if item.strip()}


settings = Settings()
