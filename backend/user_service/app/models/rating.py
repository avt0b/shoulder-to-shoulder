from datetime import datetime

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRating(Base):
    __tablename__ = "user_ratings"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    empathy_score = Column(Integer, default=0, nullable=False)
    reliability_score = Column(Float, default=100.0, nullable=False)

    total_events = Column(Integer, default=0, nullable=False)
    completed_events = Column(Integer, default=0, nullable=False)

    last_updated = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="rating")

    def __repr__(self) -> str:
        return (
            f"<UserRating(user_id={self.user_id}, "
            f"empathy={self.empathy_score}, reliability={self.reliability_score:.2f})>"
        )