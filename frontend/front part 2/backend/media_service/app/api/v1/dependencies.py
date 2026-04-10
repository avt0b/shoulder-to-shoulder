from backend.media_service.app.core.database import get_db
from backend.media_service.app.repositories.media_repository import MediaRepository
from fastapi import Depends


def get_media_repo(db=Depends(get_db)) -> MediaRepository:
    return MediaRepository(db)
