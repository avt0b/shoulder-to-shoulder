import json
import logging
from nats.aio.client import Client as NATS
from backend.event_service.app.core.config import settings

logger = logging.getLogger(__name__)
nc = NATS()

async def connect_nats():
    await nc.connect(servers=[settings.NATS_URL], name="event_service")
    logger.info(f"Connected to NATS at {settings.NATS_URL}")

async def close_nats():
    await nc.close()

async def publish_event(subject: str, payload: dict):
    await nc.publish(subject, json.dumps(payload).encode())

async def request_nats(subject: str, payload: dict, timeout: float = 3.0) -> dict:
    try:
        msg = await nc.request(subject, json.dumps(payload).encode(), timeout=timeout)
        return json.loads(msg.data.decode())
    except Exception as e:
        logger.error(f"NATS request failed [{subject}]: {e}")
        raise RuntimeError("Auth service unavailable")
