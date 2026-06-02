import os

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,"
    "http://localhost:5173,"
    "http://127.0.0.1:3000,"
    "http://127.0.0.1:5173"
)


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS") or os.getenv("ALLOWED_ORIGINS") or DEFAULT_CORS_ORIGINS
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if "*" in origins and environment in {"prod", "production"}:
        raise RuntimeError("Wildcard CORS is not allowed in production")

    return origins


def cors_allow_credentials(origins: list[str]) -> bool:
    return "*" not in origins
