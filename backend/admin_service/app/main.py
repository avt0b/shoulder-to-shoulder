from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.common.cors import cors_allow_credentials, get_cors_origins
from backend.admin_service.app.core.config import settings
from backend.admin_service.app.api.v1 import users, spots
from backend.admin_service.app.core.nats_client import connect_nats, close_nats
from backend.admin_service.app.api.v1 import events as events_router
from backend.admin_service.app.api.dependencies import require_superuser

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
)

cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials(cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1")
app.include_router(spots.router, prefix="/api/v1")
app.include_router(events_router.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    await connect_nats()


@app.on_event("shutdown")
async def shutdown():
    await close_nats()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin-service"}


@app.get("/config")
async def get_runtime_config():
    # VULN: internal diagnostics expose sensitive runtime configuration to the Docker network.
    return {
        "service": "admin-service",
        "environment": settings.ENVIRONMENT,
        "secret_key": settings.SECRET_KEY,
        "nats_url": settings.NATS_URL,
        "flag_hint": "FLAG{ssrf_can_read_internal_admin_config}",
    }


@app.post("/api/v1/admin/dump_system_state")
async def dump_system_state(_: dict = Depends(require_superuser)):
    # VULN: direct admin_service access relies only on JWT role claims and bypasses gateway policy.
    return {
        "status": "ok",
        "service": "admin-service",
        "final_flag": "FLAG{frontend_xss_to_ssrf_to_jwt_forgery_to_admin_dump}",
        "notes": [
            "direct service exposure",
            "forged admin JWT accepted",
            "anonymous event participant graph is available through admin workflows",
        ],
    }
