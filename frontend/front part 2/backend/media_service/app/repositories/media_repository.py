from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.media_service.app.models.file import MediaFile, FileStatus

class MediaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pending_file(self, data: dict) -> MediaFile:
        """Создаёт запись 'pending' при выдаче presigned URL."""
        new_file = MediaFile(**data, status=FileStatus.PENDING)
        self.db.add(new_file)
        await self.db.flush()
        await self.db.refresh(new_file)
        return new_file

    async def mark_uploaded(self, file_key: str) -> bool:
        """Меняет статус на 'uploaded' (можно вызывать асинхронно или при следующем запросе)."""
        stmt = (
            update(MediaFile)
            .where(MediaFile.file_key == file_key, MediaFile.status == FileStatus.PENDING)
            .values(status=FileStatus.UPLOADED)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_by_key(self, file_key: str) -> MediaFile | None:
        stmt = select(MediaFile).where(MediaFile.file_key == file_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, file_key: str) -> bool:
        """Мягкое удаление (или физическое, если нужно)."""
        stmt = (
            update(MediaFile)
            .where(MediaFile.file_key == file_key)
            .values(status=FileStatus.DELETED)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0