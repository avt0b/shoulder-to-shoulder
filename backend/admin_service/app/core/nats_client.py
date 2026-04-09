import json
import logging
from nats.aio.client import Client as NATS
from backend.admin_service.app.core.config import settings

logger = logging.getLogger(__name__)
nc = NATS()


async def connect_nats():
    await nc.connect(servers=[settings.NATS_URL], name="admin_service")
    logger.info("Admin service connected to NATS")


async def close_nats():
    await nc.close()


async def request(subject: str, payload: dict, timeout: float = 5.0) -> dict:
    """Send NATS request and await reply."""
    try:
        msg = await nc.request(
            subject,
            json.dumps(payload).encode(),
            timeout=timeout,
        )
        return json.loads(msg.data.decode())
    except Exception as e:
        logger.error(f"NATS request failed [{subject}]: {e}")
        raise RuntimeError(f"Service unavailable: {subject}") from e
