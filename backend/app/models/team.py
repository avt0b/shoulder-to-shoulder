import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True
    )
    password_hash: Mapped[str]
    score: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    ban_reason: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )
    banned_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Team {self.name} (score={self.score})>"


class Flag(Base):
    __tablename__ = "flags"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    flag: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        index=True
    )
    points: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="flag",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Flag {self.points}pts>"


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("ix_submissions_team_id", "team_id"),
        Index("ix_submissions_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False
    )
    flag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("flags.id"),
        nullable=True
    )
    flag_text: Mapped[str] = mapped_column(String(256))
    correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        back_populates="submissions"
    )
    flag: Mapped["Flag"] = relationship(
        back_populates="submissions"
    )

    def __repr__(self) -> str:
        return f"<Submission {'✓' if self.correct else '✗'}>"
