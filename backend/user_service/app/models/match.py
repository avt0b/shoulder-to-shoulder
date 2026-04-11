import uuid
import enum
from sqlalchemy import Column, String, Integer, Text, DateTime, func, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.user_service.app.core.database import Base


class RequestStatus(str, enum.Enum):
    OPEN = "open"  # Заявка активна, ищем напарника
    CLOSED = "closed"  # Нашли / отменили
    EXPIRED = "expired"  # Время прошло


class ResponseStatus(str, enum.Enum):
    PENDING = "pending"  # Ждём ответа автора
    ACCEPTED = "accepted"  # Автор согласен
    DECLINED = "declined"  # Отказ


# 1. Заявка в общий пул (то, что видят все)
class WorkoutRequest(Base):
    __tablename__ = "workout_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Параметры тренировки
    city = Column(String(100), nullable=False, index=True)
    preferred_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    fitness_level = Column(String(50), nullable=True)  # beginner/intermediate/advanced
    description = Column(Text, nullable=True)

    # Статус
    status = Column(String(20), default=RequestStatus.OPEN, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# 2. Отклик на заявку (приватный, виден только автору)
class RequestResponse(Base):
    __tablename__ = "request_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("workout_requests.id"), nullable=False, index=True)
    responder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    message = Column(Text, nullable=True)
    status = Column(String(20), default=ResponseStatus.PENDING, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())