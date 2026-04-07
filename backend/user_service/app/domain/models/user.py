"""SQLAlchemy model for the main User entity."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.orm import relationship

from backend.user_service.app.core.database import Base


class User(Base):
    """Main User model. Phone number is the primary login identifier."""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Основной идентификатор для входа
    phone_number = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    # Email теперь опциональный
    email = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)

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

    # Relationships
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    rating = relationship(
        "UserRating",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone_number={self.phone_number})>"