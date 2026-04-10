"""NATS client for event-driven communication."""

import json
import logging
from uuid import UUID
from jose import jwt, JWTError, ExpiredSignatureError
from nats.aio.client import Client as NATS

from backend.user_service.app.core.config import settings
from backend.user_service.app.core.database import AsyncSessionLocal
from backend.user_service.app.core.permissions import UserRole
from backend.user_service.app.repositories.badge_repository import UserBadgeRepository
from backend.user_service.app.repositories.user_repository import UserRepository
from backend.user_service.app.repositories.rating_repository import UserRatingRepository
from backend.user_service.app.services.user_service import UserService
from backend.user_service.app.core.permissions import has_permission
from backend.user_service.app.services.badge_service import evaluate_and_award_badges

logger = logging.getLogger(__name__)
nc = NATS()


nats_connected = False


async def connect_nats():
    """Connect to NATS server."""
    global nats_connected
    try:
        await nc.connect(
            servers=[settings.NATS_URL],
            name="user_service",
            reconnect_time_wait=2,
            max_reconnect_attempts=3,
            connect_timeout=2,
        )
        nats_connected = True
        logger.info(f"Connected to NATS at {settings.NATS_URL}")
    except Exception as e:
        nats_connected = False
        logger.warning(f"NATS unavailable, running without event bus: {e}")


async def close_nats():
    """Close NATS connection."""
    if nats_connected:
        await nc.close()
        logger.info("NATS connection closed")


async def _safe_subscribe(topic, cb, description="subscription"):
    """Subscribe only if connected to NATS."""
    if not nats_connected:
        return
    try:
        await nc.subscribe(topic, cb=cb)
        logger.info(f"Subscribed to {topic}")
    except Exception as e:
        logger.error(f"Failed to subscribe to {topic}: {e}")


async def setup_nats_subscribers():
    """Subscribe to relevant NATS topics."""
    if not nats_connected:
        logger.info("Skipping NATS subscribers (not connected)")
        return
    await nc.subscribe("workout.completed", cb=handle_workout_event)
    await nc.subscribe("empathy.awarded", cb=handle_empathy_event)
    await nc.subscribe("auth.validate_token", cb=handle_auth_validate_token)
    logger.info("NATS subscribers registered")


async def setup_admin_subscribers():
    if not nats_connected:
        logger.info("Skipping admin subscribers (not connected)")
        return
    await nc.subscribe("admin.user.list", cb=handle_admin_user_list)
    await nc.subscribe("admin.user.ban", cb=handle_admin_user_ban)
    await nc.subscribe("admin.user.unban", cb=handle_admin_user_unban)
    await nc.subscribe("admin.user.award_badge", cb=handle_admin_award_badge)
    await nc.subscribe("admin.user.check_permission", cb=handle_admin_check_permission)
    logger.info("Admin command subscribers registered")


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
            badge_repo = UserBadgeRepository(db)
            user_service = UserService(user_repo, None, rating_repo, badge_repo)
            rating = await user_service.update_reliability(user_id, success)
            if not rating:
                logger.warning(f"User {user_id} not found for reliability update")
                return
            awarded = await evaluate_and_award_badges(user_id, {
                "completed_events": rating.completed_events,
                "total_events": rating.total_events,
                "reliability_score": rating.reliability_score,
                "empathy_score": rating.empathy_score,
            }, db)

            await db.commit()
            if awarded:
                logger.info(f"User {user_id} earned badges: {awarded}")
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


async def handle_admin_user_list(msg):
    data = json.loads(msg.data.decode())
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            users = await user_repo.get_all(
                limit=data.get("limit", 50),
                offset=data.get("offset", 0),
                search=data.get("search"),
            )
            users_serializable = [
                {
                    "id": str(u.id),
                    "phone_number": u.phone_number,
                    "email": u.email,
                    "is_active": u.is_active,
                    "is_phone_verified": u.is_phone_verified,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "updated_at": u.updated_at.isoformat() if u.updated_at else None,
                }
                for u in users
            ]

            await msg.respond(json.dumps({"ok": True, "data": users_serializable}).encode())

    except Exception as e:
        logger.exception("Admin list users failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_user_ban(msg):
    data = json.loads(msg.data.decode())
    user_id_raw = data.get("user_id")
    reason = data.get("reason")

    try:
        user_id = UUID(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
    except (ValueError, AttributeError):
        await msg.respond(json.dumps({"ok": False, "error": f"Invalid UUID: {user_id_raw}"}).encode())
        return

    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            success = await user_repo.set_active(str(user_id), is_active=False)

            if not success:
                await msg.respond(json.dumps({"ok": False, "error": "User not found"}).encode())
                return

            await db.commit()
            log_msg = f"Admin banned user {user_id}" + (f" (reason: {reason})" if reason else "")
            logger.info(log_msg)

            await msg.respond(json.dumps({"ok": True, "data": {"status": "banned"}}).encode())

    except Exception as e:
        logger.exception("Admin ban user failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_user_unban(msg):
    data = json.loads(msg.data.decode())
    user_id_raw = data.get("user_id")
    comment = data.get("comment")

    try:
        user_id = UUID(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
    except (ValueError, AttributeError):
        await msg.respond(json.dumps({"ok": False, "error": f"Invalid UUID: {user_id_raw}"}).encode())
        return

    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            success = await user_repo.set_active(str(user_id), is_active=True)

            if not success:
                await msg.respond(json.dumps({"ok": False, "error": "User not found"}).encode())
                return

            await db.commit()
            log_msg = f"Admin unbanned user {user_id}" + (f" (comment: {comment})" if comment else "")
            logger.info(log_msg)

            await msg.respond(json.dumps({"ok": True, "data": {"status": "unbanned"}}).encode())

    except Exception as e:
        logger.exception("Admin unban user failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_award_badge(msg):
    """Handle admin.user.award_badge request: award badge to user."""
    data = json.loads(msg.data.decode())
    user_id_raw = data.get("user_id")
    badge_type = data.get("badge_type")

    if not badge_type:
        await msg.respond(json.dumps({"ok": False, "error": "badge_type is required"}).encode())
        return

    try:
        user_id = UUID(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
    except (ValueError, AttributeError):
        await msg.respond(json.dumps({"ok": False, "error": f"Invalid UUID: {user_id_raw}"}).encode())
        return

    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            badge_repo = UserBadgeRepository(db)  # TODO: добавить, когда сделаем

            user = await user_repo.get_by_id(str(user_id))
            if not user:
                await msg.respond(json.dumps({"ok": False, "error": "User not found"}).encode())
                return

            badge = await badge_repo.award(str(user_id), badge_type)
            await db.commit()

            if badge:
                logger.info(f"Admin awarded badge '{badge_type}' to user {user_id}")
                await msg.respond(
                    json.dumps({"ok": True, "data": {"badge_type": badge_type, "awarded": True}}).encode())
            else:
                logger.info(f"Badge '{badge_type}' already exists for user {user_id}")
                await msg.respond(json.dumps({"ok": True, "data": {"badge_type": badge_type, "awarded": False,
                                                                   "message": "Already exists"}}).encode())

    except Exception as e:
        logger.exception("Admin award badge failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_check_permission(msg):
    data = json.loads(msg.data.decode())
    user_id_raw = data.get("user_id")
    required_role = data.get("required_role", "user")

    try:
        user_id = UUID(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
    except (ValueError, AttributeError):
        await msg.respond(json.dumps({"ok": False, "error": "Invalid UUID"}).encode())
        return

    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_id(str(user_id))

            if not user:
                await msg.respond(json.dumps({"ok": False, "error": "User not found"}).encode())
                return
            user_role: UserRole = user.role or "user"
            allowed = has_permission(user_role, required_role)

            await msg.respond(json.dumps({
                "ok": True,
                "data": {
                    "allowed": allowed,
                    "user_role": user_role,
                    "is_active": user.is_active,
                }
            }).encode())

    except Exception as e:
        logger.exception("Permission check failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_auth_validate_token(msg):
    data = json.loads(msg.data.decode())
    token = data.get("token")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing subject")

        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                await msg.respond(json.dumps({"ok": False, "error": "Account banned or not found"}).encode())
                return

        await msg.respond(json.dumps({
            "ok": True,
            "data": {
                "user_id": user_id,
                "is_active": True,
                "role": user.role or "user"
            }
        }).encode())

    except ExpiredSignatureError:
        await msg.respond(json.dumps({"ok": False, "error": "Token expired"}).encode())
    except JWTError:
        await msg.respond(json.dumps({"ok": False, "error": "Invalid token"}).encode())
    except Exception as e:
        logger.exception("Auth validation failed")
        await msg.respond(json.dumps({"ok": False, "error": "Internal auth error"}).encode())


async def setup_nats_subscribers():
    """Subscribe to relevant NATS topics."""
    await nc.subscribe("workout.completed", cb=handle_workout_event)
    await nc.subscribe("empathy.awarded", cb=handle_empathy_event)
    await nc.subscribe("auth.validate_token", cb=handle_auth_validate_token)
    logger.info("NATS subscribers registered")


async def setup_admin_subscribers():
    await nc.subscribe("admin.user.list", cb=handle_admin_user_list)
    await nc.subscribe("admin.user.ban", cb=handle_admin_user_ban)
    await nc.subscribe("admin.user.unban", cb=handle_admin_user_unban)
    await nc.subscribe("admin.user.award_badge", cb=handle_admin_award_badge)
    await nc.subscribe("admin.user.check_permission", cb=handle_admin_check_permission)
    logger.info("Admin command subscribers registered")
