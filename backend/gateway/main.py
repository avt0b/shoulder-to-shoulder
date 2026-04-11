import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .core.http_client import http_client
from .api.v1.endpoints.router import router as aggregated_router
from .api.v1.endpoints.user_router import router_auth, router_users
from .api.v1.endpoints.event_router import router_events
from .api.v1.endpoints.admin_router import router_admin
from .api.v1.endpoints.media_router import router_media
from .api.v1.endpoints.notification_router import router_notifications

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway starting up...")
    connected = await http_client.connect()
    if not connected:
        logger.error("❌ Failed to connect to HTTP client")
    yield
    logger.info("🛑 Gateway shutting down...")
    await http_client.disconnect()


app = FastAPI(
    title="S2S API Gateway",
    version=settings.app_version,
    description="API Gateway for microservices communication",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_prefix = settings.api_v1_prefix

app.include_router(router_auth, prefix=api_v1_prefix)
app.include_router(router_users, prefix=api_v1_prefix)
app.include_router(router_events, prefix=api_v1_prefix)
app.include_router(router_admin, prefix=api_v1_prefix)
app.include_router(router_media, prefix=api_v1_prefix)
app.include_router(router_notifications, prefix=api_v1_prefix)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": "gateway",
        "http_client_ready": http_client.is_connected
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "service": "S2S API Gateway",
        "version": settings.app_version,
        "docs": "/docs"
    }
