"""NATS client for event-driven communication."""

import json
import logging
from nats.aio.client import Client as NATS

from backend.user_service.app.core.config import settings
from backend.user_service.app.core.database import AsyncSessionLocal
from backend.user_service.app.repositories.user_repository import UserRepository
from backend.user_service.app.repositories.rating_repository import UserRatingRepository
from backend.user_service.app.services.user_service import UserService

logger = logging.getLogger(__name__)
nc = NATS()


async def connect_nats():
    """Connect to NATS server."""
    try:
        await nc.connect(
            servers=[settings.NATS_URL],
            name="user_service",
            reconnect_time_wait=2,
            max_reconnect_attempts=10,
        )
        logger.info(f"Connected to NATS at {settings.NATS_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to NATS: {e}")


async def close_nats():
    """Close NATS connection."""
    await nc.close()
    logger.info("NATS connection closed")


async def handle_workout_event(msg):
    """Handle workout.completed event from Event Service."""
    try:
        data = json.loads(msg.data.decode())
        user_id = data.get("user_id")
        success = data.get("success", True)

        if not user_id:
            logger.warning("Received workout event without user_id")
            return

        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            rating_repo = UserRatingRepository(db)
            user_service = UserService(user_repo, None, rating_repo, None)

            await user_service.update_reliability(user_id, success)
            await db.commit()

        logger.info(f"Updated reliability for user {user_id}: success={success}")

    except Exception as e:
        logger.error(f"Error handling workout event: {e}")


async def handle_empathy_event(msg):
    """Handle empathy.awarded event from Event Service."""
    try:
        data = json.loads(msg.data.decode())
        user_id = data.get("user_id")
        points = data.get("points", 1)

        if not user_id:
            logger.warning("Received empathy event without user_id")
            return

        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            rating_repo = UserRatingRepository(db)
            user_service = UserService(user_repo, None, rating_repo, None)

            await user_service.add_empathy_points(user_id, points)
            await db.commit()

        logger.info(f"Added {points} empathy points for user {user_id}")

    except Exception as e:
        logger.error(f"Error handling empathy event: {e}")


async def setup_nats_subscribers():
    """Subscribe to relevant NATS topics."""
    await nc.subscribe("workout.completed", cb=handle_workout_event)
    await nc.subscribe("empathy.awarded", cb=handle_empathy_event)
    logger.info("NATS subscribers registered")
