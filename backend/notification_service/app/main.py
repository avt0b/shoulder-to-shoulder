"""Notification Service FastAPI application."""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1 import notifications
from app.core.database import init_db
from app.core.nats_client import nats_client
from app.workers.scheduler import start_scheduler, stop_scheduler

# API tags metadata
tags_metadata = [
    {
        "name": "notifications",
        "description": "Notification management endpoints",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Initialize database
    await init_db()

    # Initialize NATS client
    await nats_client.connect()

    # Start background scheduler
    await start_scheduler()

    yield

    # Cleanup on shutdown
    await stop_scheduler()
    await nats_client.disconnect()


app = FastAPI(
    title="Notification Service",
    description="Реактивный сервис управления уведомлениями для Плечом к плечу",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Include routers
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification_service"}
