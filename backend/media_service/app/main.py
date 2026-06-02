from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.common.cors import cors_allow_credentials, get_cors_origins
from backend.media_service.app.core.config import settings
from backend.media_service.app.core.database import Base, engine
from backend.media_service.app.models.file import MediaFile  # noqa: F401
from backend.media_service.app.api.v1.media import router as media_router

app = FastAPI(title=settings.PROJECT_NAME, docs_url="/docs")

cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials(cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(media_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "media-service"}
