import asyncio
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api import admin, auth, flags, scoreboard, submissions, team
from app.core.config import settings
from app.core.database import engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if settings.AUTO_CREATE_TABLES:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text(
                "ALTER TABLE flags ADD COLUMN IF NOT EXISTS title VARCHAR(160) NOT NULL DEFAULT 'Untitled task'"
            ))
            await conn.execute(text(
                "ALTER TABLE flags ADD COLUMN IF NOT EXISTS text TEXT"
            ))
            await conn.execute(text(
                "ALTER TABLE flags ADD COLUMN IF NOT EXISTS image_url VARCHAR(1024)"
            ))
            await conn.execute(text(
                "ALTER TABLE flags ADD COLUMN IF NOT EXISTS is_visible BOOLEAN NOT NULL DEFAULT TRUE"
            ))
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(team.router)
app.include_router(flags.router)
app.include_router(submissions.router)
app.include_router(scoreboard.router)
app.include_router(admin.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": message, "status": exc.status_code},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "status": 422,
            "detail": exc.errors(),
        },
    )


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
