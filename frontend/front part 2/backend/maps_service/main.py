from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# from src.core.config import cors_settings
# from src.core.infrastructure.database.database import engine, get_session
# from src.core.infrastructure.exception_handler import register_handlers
from logger import get_logger
# from src.modules.identity.presentation.api.router import router as account_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application startup: initializing")

    try:
        yield
    finally:
        logger.info("Application shutdown: cleaning up...")

        if engine is not None:
            try:
                await engine.dispose()
                logger.info("Database connections closed successfully")
            except Exception as e:
                logger.error(f"Failed to close database connections: {e}", exc_info=True)

        logger.info("Application shutdown complete")


app = FastAPI(title="KYOP API", description="Keep Your Own Pace Backend API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_handlers(app)

app.include_router(account_router)


@app.get("/health", tags=["system"])
async def health_check(db: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """
    Checks connection to database
    """
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}


# запуск minio локально для проверки:
# minio.exe server D:\data-for-minio --console-address ":9001" --license D:/minio.license
