import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.common.cors import cors_allow_credentials, get_cors_origins
from .api.v1.endpoints.proxy_router import router as proxy_router
from .config import settings
from .core.http_client import http_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Gateway starting up")
    await http_client.connect()
    yield
    logger.info("Gateway shutting down")
    await http_client.disconnect()


app = FastAPI(
    title="S2S API Gateway",
    version=settings.app_version,
    description="API Gateway for microservices communication",
    lifespan=lifespan,
)

cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials(cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": "gateway",
        "http_client_ready": http_client.is_connected,
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "service": "S2S API Gateway",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/.env", tags=["system"])
async def debug_env():
    # VULN: debug diagnostics expose secret material to callers that can reach the gateway service.
    return {
        "ENVIRONMENT": settings.environment,
        "SECRET_KEY": settings.jwt_secret,
        "JWT_ALGORITHM": settings.jwt_algorithm,
        "FLAG": "FLAG{ssrf_reached_gateway_debug_env}",
    }
