import uuid
import enum
from sqlalchemy import Column, String, BigInteger, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.media_service.app.core.database import Base


class FilePurpose(str, enum.Enum):
    AVATAR = "avatar"
    EVENT = "event"
    SPOT = "spot"
    BADGE = "badge"


class FileStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    DELETED = "deleted"


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ключи и владелец
    file_key = Column(String(255), unique=True, nullable=False, index=True)  # S3 key
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Кто загрузил
    purpose = Column(String(20), nullable=False)  # avatar/event/...

    # Мета-инфа
    content_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    status = Column(String(20), default=FileStatus.PENDING, nullable=False)

    # Публичная ссылка (кэшируем, чтобы не собирать вручную)
    public_url = Column(String(512), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())