import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.common.cors import cors_allow_credentials, get_cors_origins
from .api.v1.endpoints import places_router, routes_router
from .config import settings
from .database import Base, engine

logger = logging.getLogger(__name__)

logger.info("DATABASE_URL: %s", settings.DATABASE_URL)
logger.info("POSTGRES_HOST: %s", settings.POSTGRES_HOST)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Maps Service для Shoulder to Shoulder",
)

cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials(cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text(
                "ALTER TABLE places ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE"
            ))
        logger.info("Database tables initialized")
    except Exception:
        logger.exception("Database initialization failed")
        raise


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    logger.info("Maps service stopped")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": "maps_service",
    }


api_v1_prefix = settings.API_V1_PREFIX

app.include_router(places_router, prefix=api_v1_prefix)
app.include_router(routes_router, prefix=api_v1_prefix)


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
