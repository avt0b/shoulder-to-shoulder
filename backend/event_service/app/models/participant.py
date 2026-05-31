import uuid, enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.event_service.app.core.database import Base

class ParticipantStatus(str, enum.Enum):
    JOINED = "joined"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"
    MISSED = "missed"

class EventParticipant(Base):
    __tablename__ = "event_participants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(20), default=ParticipantStatus.JOINED, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
