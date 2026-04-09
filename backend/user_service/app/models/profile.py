from datetime import datetime

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship

from backend.user_service.app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    display_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    fitness_level = Column(String(20), default="beginner", nullable=False)
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    preferences = Column(JSON, default=dict, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, display_name={self.display_name})>"