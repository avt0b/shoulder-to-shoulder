from nats.aio.client import Client as NATS
from backend.event_service.app.core.config import settings
from nats.errors import NoServersError, TimeoutError, ConnectionClosedError
import json
import logging
from uuid import UUID
from sqlalchemy import select, update, delete, func
from backend.event_service.app.core.database import AsyncSessionLocal
from backend.event_service.app.models.event import Event
from backend.event_service.app.models.participant import EventParticipant

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


async def handle_admin_event_list(msg):
    data = json.loads(msg.data.decode())
    try:
        limit = min(data.get("limit", 50), 100)
        offset = data.get("offset", 0)
        status_filter = data.get("status")
        host_id = data.get("host_id")
        spot_id = data.get("spot_id")

        async with AsyncSessionLocal() as db:
            stmt = select(Event)
            if status_filter:
                stmt = stmt.where(Event.status == status_filter)
            if host_id:
                stmt = stmt.where(Event.host_id == UUID(host_id))
            if spot_id:
                stmt = stmt.where(Event.spot_id == UUID(spot_id))
            stmt = stmt.order_by(Event.created_at.desc()).offset(offset).limit(limit)

            result = await db.execute(stmt)
            events = result.scalars().all()

            events_serializable = []
            for e in events:
                count_stmt = select(func.count()).select_from(EventParticipant).where(
                    EventParticipant.event_id == e.id,
                    EventParticipant.status != "cancelled"
                )
                count_result = await db.execute(count_stmt)
                events_serializable.append({
                    "id": str(e.id),
                    "host_id": str(e.host_id),
                    "spot_id": str(e.spot_id),
                    "title": e.title,
                    "description": e.description,
                    "max_participants": e.max_participants,
                    "duration_minutes": e.duration_minutes,
                    "status": e.status,
                    "start_time": e.start_time.isoformat(),
                    "photo_url": e.photo_url,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                    "participant_count": count_result.scalar()
                })

            await msg.respond(json.dumps({"ok": True, "data": events_serializable}).encode())

    except Exception as e:
        logger.exception("Admin list events failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_event_get(msg):
    data = json.loads(msg.data.decode())
    try:
        event_id = UUID(data["event_id"])
        async with AsyncSessionLocal() as db:
            stmt = select(Event).where(Event.id == event_id)
            result = await db.execute(stmt)
            event = result.scalar_one_or_none()

            if not event:
                await msg.respond(json.dumps({"ok": False, "error": "Event not found"}).encode())
                return

            count_stmt = select(func.count()).select_from(EventParticipant).where(
                EventParticipant.event_id == event.id,
                EventParticipant.status != "cancelled"
            )
            count_result = await db.execute(count_stmt)

            await msg.respond(json.dumps({
                "ok": True,
                "data": {
                    "id": str(event.id),
                    "host_id": str(event.host_id),
                    "spot_id": str(event.spot_id),
                    "title": event.title,
                    "description": event.description,
                    "max_participants": event.max_participants,
                    "duration_minutes": event.duration_minutes,
                    "status": event.status,
                    "start_time": event.start_time.isoformat(),
                    "photo_url": event.photo_url,
                    "created_at": event.created_at.isoformat() if event.created_at else None,
                    "participant_count": count_result.scalar()
                }
            }).encode())

    except Exception as e:
        logger.exception("Admin get event failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_event_delete(msg):
    data = json.loads(msg.data.decode())
    try:
        event_id = UUID(data["event_id"])
        async with AsyncSessionLocal() as db:
            stmt = delete(Event).where(Event.id == event_id)
            result = await db.execute(stmt)
            await db.commit()

            if result.rowcount == 0:
                await msg.respond(json.dumps({"ok": False, "error": "Event not found"}).encode())
                return

            await msg.respond(json.dumps({"ok": True, "data": {"status": "deleted"}}).encode())

    except Exception as e:
        logger.exception("Admin delete event failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def handle_admin_event_update(msg):
    data = json.loads(msg.data.decode())
    try:
        event_id = UUID(data["event_id"])
        update_fields = {}
        allowed = {"title", "description", "max_participants", "duration_minutes", "start_time", "photo_url",
                   "status"}

        for key in allowed:
            if key in data and data[key] is not None:
                if key == "start_time":
                    from datetime import datetime
                    update_fields[key] = datetime.fromisoformat(data[key].replace("Z", "+00:00"))
                else:
                    update_fields[key] = data[key]

        if not update_fields:
            await msg.respond(json.dumps({"ok": False, "error": "No valid fields to update"}).encode())
            return

        async with AsyncSessionLocal() as db:
            stmt = (
                update(Event)
                .where(Event.id == event_id)
                .values(**update_fields)
                .returning(Event)
            )
            result = await db.execute(stmt)
            await db.commit()
            event = result.scalar_one_or_none()

            if not event:
                await msg.respond(json.dumps({"ok": False, "error": "Event not found"}).encode())
                return

            await msg.respond(json.dumps({
                "ok": True,
                "data": {
                    "id": str(event.id),
                    "title": event.title,
                    "status": event.status,
                    "updated_at": event.updated_at.isoformat() if event.updated_at else None
                }
            }).encode())

    except Exception as e:
        logger.exception("Admin update event failed")
        await msg.respond(json.dumps({"ok": False, "error": str(e)}).encode())


async def setup_admin_event_subscribers(nats):
    nats.nc.subscribe("admin.event.list", cb=handle_admin_event_list)
    nats.nc.subscribe("admin.event.get", cb=handle_admin_event_get)
    nats.nc.subscribe("admin.event.delete", cb=handle_admin_event_delete)
    nats.nc.subscribe("admin.event.update", cb=handle_admin_event_update)
    logger.info("Admin event subscribers registered")
