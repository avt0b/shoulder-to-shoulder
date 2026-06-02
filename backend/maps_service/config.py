from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache
import sys


class Settings(BaseSettings):

    DATABASE_URL: str = ""
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_DB: str = "shoulder_to_shoulder_db"
    POSTGRES_PORT: int = 5432
    DB_ECHO: bool = False
    
    API_V1_PREFIX: str = "/api/v1"
    APP_NAME: str = "Maps Service"
    APP_VERSION: str = "0.1.0"
    
    MIN_LATITUDE: float = -90.0
    MAX_LATITUDE: float = 90.0
    MIN_LONGITUDE: float = -180.0
    MAX_LONGITUDE: float = 180.0
    
    DEFAULT_ZOOM: int = 14
    SEARCH_RADIUS_KM: float = 5.0
    
    OPENROUTER_API_KEY: str = ""
    OPENROUTE_SERVICE_API_KEY: str = ""
    
    # Proxy settings (optional)
    PROXY_ENABLED: bool = False
    PROXY_URL: str = "socks5h://127.0.0.1:10809"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Собирает DATABASE_URL из компонентов если он не задан"""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        # Логирование в stdout/stderr 
        print(f"[CONFIG] DATABASE_URL: {self.DATABASE_URL}", file=sys.stderr)
        print(f"[CONFIG] POSTGRES_HOST: {self.POSTGRES_HOST}", file=sys.stderr)
        print(f"[CONFIG] POSTGRES_DB: {self.POSTGRES_DB}", file=sys.stderr)
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
