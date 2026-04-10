from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.media_service.app.core.config import settings
from backend.media_service.app.api.v1.media import router as media_router

app = FastAPI(title=settings.PROJECT_NAME, docs_url="/docs")

#TODO: Ксюше - поменять
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(media_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "media-service"}
