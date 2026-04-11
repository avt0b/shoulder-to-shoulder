from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.user_service.app.models.match import WorkoutRequest, RequestResponse, RequestStatus
from backend.user_service.app.models.user import User
from backend.user_service.app.models.profile import UserProfile
from backend.user_service.app.models.rating import UserRating
from datetime import datetime, timezone


class PoolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- ЧТЕНИЕ ПУЛА (для всех) ---
    async def get_open_requests(self, city: str | None = None, limit: int = 20) -> list[dict]:
        """Возвращает список активных заявок из пула."""
        stmt = (
            select(
                WorkoutRequest.id,
                WorkoutRequest.city,
                WorkoutRequest.preferred_time,
                WorkoutRequest.duration_minutes,
                WorkoutRequest.fitness_level,
                WorkoutRequest.description,
                User.id.label("author_id"),
                UserProfile.display_name,
                UserProfile.avatar_url,
                UserRating.reliability_score,
            )
            .join(User, User.id == WorkoutRequest.user_id)
            .join(UserProfile, UserProfile.user_id == User.id)
            .join(UserRating, UserRating.user_id == User.id)
            .where(WorkoutRequest.status == RequestStatus.OPEN)
            .order_by(WorkoutRequest.preferred_time.asc())
            .limit(limit)
        )
        if city:
            stmt = stmt.where(WorkoutRequest.city.ilike(f"%{city}%"))

        result = await self.db.execute(stmt)
        return [
            {
                "request_id": str(row.id),
                "author_id": str(row.author_id),
                "author_name": row.display_name,
                "avatar_url": row.avatar_url,
                "reliability": float(row.reliability_score),
                "city": row.city,
                "time": row.preferred_time,
                "duration": row.duration_minutes,
                "level": row.fitness_level,
                "desc": row.description,
            }
            for row in result.all()
        ]

    # --- СОЗДАНИЕ ЗАЯВКИ ---
    async def create_request(self, user_id: UUID, data: dict) -> WorkoutRequest:
        req = WorkoutRequest(user_id=user_id, **data, status=RequestStatus.OPEN)
        self.db.add(req)
        await self.db.flush()
        return req

    # --- ОТКЛИК НА ЗАЯВКУ ---
    async def create_response(self, request_id: UUID, responder_id: UUID, message: str | None) -> RequestResponse:
        # Проверка: не откликается ли автор на свою же заявку
        req = await self.db.get(WorkoutRequest, request_id)
        if req and req.user_id == responder_id:
            raise ValueError("Cannot respond to your own request")

        resp = RequestResponse(request_id=request_id, responder_id=responder_id, message=message)
        self.db.add(resp)
        await self.db.flush()
        return resp

    # --- УПРАВЛЕНИЕ ДЛЯ АВТОРА ---
    async def get_my_incoming_responses(self, user_id: UUID) -> list[dict]:
        """Автор видит, кто откликнулся на ЕГО заявки."""
        stmt = (
            select(
                RequestResponse.id,
                RequestResponse.message,
                RequestResponse.status,
                RequestResponse.created_at,
                User.id.label("responder_id"),
                UserProfile.display_name,
                UserProfile.avatar_url,
                WorkoutRequest.id.label("request_id"),
                WorkoutRequest.preferred_time,
            )
            .join(WorkoutRequest, WorkoutRequest.id == RequestResponse.request_id)
            .join(User, User.id == RequestResponse.responder_id)
            .join(UserProfile, UserProfile.user_id == User.id)
            .where(WorkoutRequest.user_id == user_id)  # Только мои заявки
            .order_by(RequestResponse.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return [
            {
                "response_id": str(row.id),
                "request_id": str(row.request_id),
                "responder_id": str(row.responder_id),
                "responder_name": row.display_name,
                "avatar_url": row.avatar_url,
                "message": row.message,
                "status": row.status,
                "workout_time": row.preferred_time,
            }
            for row in result.all()
        ]

    async def update_response_status(self, response_id: UUID, status: str) -> bool:
        stmt = update(RequestResponse).where(RequestResponse.id == response_id).values(status=status)
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def close_request(self, request_id: UUID):
        stmt = update(WorkoutRequest).where(WorkoutRequest.id == request_id).values(status=RequestStatus.CLOSED)
        await self.db.execute(stmt)

    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()