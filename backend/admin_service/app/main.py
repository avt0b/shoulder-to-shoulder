from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.common.cors import cors_allow_credentials, get_cors_origins
from backend.admin_service.app.core.config import settings
from backend.admin_service.app.api.v1 import users, spots
from backend.admin_service.app.core.nats_client import connect_nats, close_nats
from backend.admin_service.app.api.v1 import events as events_router

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
