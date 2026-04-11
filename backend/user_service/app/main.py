"""Main FastAPI application for User Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.user_service.app.core.config import settings
from backend.user_service.app.api.v1.auth import router as auth_router
from backend.user_service.app.api.v1.users import router as users_router
from backend.user_service.app.api.v1.matches import router as matches_router
from backend.user_service.app.core.nats_client import connect_nats, close_nats, handle_workout_event, nc, \
    setup_nats_subscribers, setup_admin_subscribers

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="User Service для приложения «Плечом к плечу»",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    # TODO: Ксюше - поменять на конкретный домен в production'е
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(matches_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    await connect_nats()
    await setup_nats_subscribers()
    await setup_admin_subscribers()


@app.on_event("shutdown")
async def shutdown():
    await close_nats()


@app.get("/")
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} is running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}
