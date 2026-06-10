from pathlib import Path
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/ctf_db"
    AUTO_CREATE_TABLES: bool = True

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ADMIN_TOKEN: str = "dev-admin-token"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    UPLOAD_DIR: str = "uploads"

    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "CTF Platform API"
    DOCS_ENABLED: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    DEBUG: bool | str = True

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = True


settings = Settings()
