import json
import logging
from nats.aio.client import Client as NATS
from backend.event_service.app.core.config import settings
from nats.errors import NoServersError, TimeoutError, ConnectionClosedError

logger = logging.getLogger(__name__)
nc = NATS()
nats_available = False


async def connect_nats():
    global nats_available
    try:
        await nc.connect(
            servers=[settings.NATS_URL],
            name="event_service",
            connect_timeout=2.0,
            max_reconnect_attempts=-1,
            reconnect_time_wait=2,
        )
        nats_available = True
        logger.info(f"Connected to NATS at {settings.NATS_URL}")
    except Exception as e:
        logger.warning(f"NATS unavailable on startup: {e}. Service will start anyway.")
        nats_available = False


async def close_nats():
    global nats_available
    if nats_available:
        await nc.close()
        nats_available = False


async def publish_event(subject: str, payload: dict):
    global nats_available
    if not nats_available:
        logger.debug("NATS disconnected, skipping publish")
        return
    try:
        await nc.publish(subject, json.dumps(payload).encode())
    except Exception as e:
        logger.error(f"NATS publish failed [{subject}]: {e}")
        nats_available = False


async def request_nats(subject: str, payload: dict, timeout: float = 3.0) -> dict:
    global nats_available
    if not nats_available:
        raise RuntimeError("Auth service unavailable (NATS disconnected)")
    try:
        msg = await nc.request(subject, json.dumps(payload).encode(), timeout=timeout)
        return json.loads(msg.data.decode())
    except (NoServersError, TimeoutError, ConnectionClosedError) as e:
        logger.error(f"NATS request failed [{subject}]: {e}")
        nats_available = False
        raise RuntimeError("Auth service unavailable")
    except Exception as e:
        logger.error(f"NATS unexpected error [{subject}]: {e}")
        raise RuntimeError("Auth service unavailable")
