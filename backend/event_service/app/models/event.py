import uuid, enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class EventStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    spot_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    max_participants = Column(Integer, default=10, nullable=False)
    duration_minutes = Column(Integer, default=60, nullable=False)
    status = Column(String(20), default=EventStatus.PENDING, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    photo_url = Column(Text, nullable=True)  # 🔜 Для совместной фотки
    created_at = Column(DateTime(timezone=True), server_default=func.now())