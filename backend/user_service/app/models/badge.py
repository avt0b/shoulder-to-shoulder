from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Badge(Base):

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    badge_type = Column(String(50), nullable=False)

    awarded_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", backref="badges")

    def __repr__(self) -> str:
        return f"<Badge(user_id={self.user_id}, type={self.badge_type})>"