"""Notification Service FastAPI application."""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.notification_service.app.core.nats_client import nats_client
from backend.notification_service.app.subscribers.event_subscriber import start_subscribers

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

    await nats_client.connect()
    await start_subscribers()

    yield

    await nats_client.disconnect()


app = FastAPI(
    title="Notification Service",
    description="Реактивный сервис управления уведомлениями для Плечом к плечу",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# # Include routers
# app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification_service"}
