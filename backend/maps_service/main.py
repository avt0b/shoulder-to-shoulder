from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .api.v1.endpoints import places_router, routes_router, events_router
from .api.v1.endpoints.meetups import router as meetups_router
from .database import Base, engine
from .utils.nats_client import NatsRpcClient

logger = logging.getLogger(__name__)

# Логируем конфигурацию при запуске
logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")
logger.info(f"NATS_SERVER: {settings.NATS_SERVER}")
logger.info(f"POSTGRES_HOST: {settings.POSTGRES_HOST}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Maps Service для Shoulder to Shoulder",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Инициализация при запуске"""
    try:
        # 1. Создаём таблицы БД
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Таблицы БД инициализированы")
    except Exception as e:
        logger.error(f"✗ Ошибка при инициализации БД: {e}")
        raise
    
    try:
        # 2. Инициализируем NATS
        nats = NatsRpcClient.get_instance()
        nats_server = getattr(settings, 'NATS_SERVER', 'nats://localhost:4222')
        
        if await nats.connect(nats_server):
            logger.info("✓ NATS клиент инициализирован")
            print("✓ NATS клиент инициализирован")
        else:
            logger.warning("⚠️ NATS не подключен - мероприятия не будут доступны")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при подключении к NATS: {e}")


@app.on_event("shutdown")
async def shutdown():
    nats = NatsRpcClient.get_instance()
    await nats.disconnect()
    
    await engine.dispose()
    logger.info("Сервис выключен")


@app.get("/health", tags=["health"])
async def health_check():
    nats = NatsRpcClient.get_instance()
    return {
        "status": "ok",
        "service": "maps_service",
        "nats_connected": nats.is_connected
    }


api_v1_prefix = settings.API_V1_PREFIX

app.include_router(places_router, prefix=api_v1_prefix)
app.include_router(routes_router, prefix=api_v1_prefix)
app.include_router(meetups_router, prefix=api_v1_prefix)
app.include_router(events_router, prefix=api_v1_prefix)


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# uvicorn backend.maps_service.main:app --port 8001