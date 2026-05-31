from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from backend.event_service.app.core.config import settings
from backend.event_service.app.api.v1.events import router as events_router
from backend.event_service.app.core.database import Base, engine
from backend.event_service.app.models.event import Event  # noqa: F401
from backend.event_service.app.models.participant import EventParticipant  # noqa: F401
from backend.event_service.app.core.nats_client import connect_nats, close_nats, setup_admin_event_subscribers
from backend.event_service.app.core.nats_client import nc as nats

app = FastAPI(title=settings.PROJECT_NAME, docs_url="/docs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(events_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ"))
        await conn.execute(text("ALTER TABLE events ADD COLUMN IF NOT EXISTS anonymous BOOLEAN DEFAULT false NOT NULL"))
        await conn.execute(text("ALTER TABLE events ALTER COLUMN spot_id DROP NOT NULL"))
        await conn.execute(text("ALTER TABLE event_participants ADD COLUMN IF NOT EXISTS photo_url TEXT"))

    await connect_nats()
    await setup_admin_event_subscribers()


@app.on_event("shutdown")
async def shutdown():
    await close_nats()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "event-service"}
