from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.event_service.app.core.config import settings
from backend.event_service.app.api.v1.events import router as events_router
from backend.event_service.app.core.nats_client import connect_nats, close_nats, setup_admin_event_subscribers
from backend.event_service.app.core.nats_client import nc as nats

app = FastAPI(title=settings.PROJECT_NAME, docs_url="/docs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(events_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    await connect_nats()
    await setup_admin_event_subscribers()


@app.on_event("shutdown")
async def shutdown():
    await close_nats()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "event-service"}
