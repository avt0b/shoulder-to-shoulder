import uuid
from fastapi import APIRouter, Depends, HTTPException
from backend.media_service.app.api.v1.dependencies import get_media_repo
from backend.media_service.app.core.s3_client import s3
from backend.media_service.app.core.config import settings
from backend.media_service.app.repositories.media_repository import MediaRepository
from backend.media_service.app.schemas.media import UploadUrlRequest, FileDeleteResponse

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload-url")
async def get_upload_url(
        req: UploadUrlRequest,
        repo: MediaRepository = Depends(get_media_repo),
):
    if req.purpose not in settings.ALLOWED_PURPOSES:
        raise HTTPException(400, detail="Invalid purpose")

    ext = req.content_type.split("/")[-1]
    file_key = f"{req.purpose}/{req.owner_id}/{uuid.uuid4().hex[:10]}.{ext}"

    s3_response = s3.generate_upload_url(file_key, req.content_type)

    await repo.create_pending_file({
        "file_key": file_key,
        "owner_id": req.owner_id,
        "purpose": req.purpose,
        "content_type": req.content_type,
        "file_size": req.file_size,
        "public_url": s3_response["public_url"]
    })

    return {
        "file_key": file_key,
        "upload_url": s3_response["upload_url"],
        "fields": s3_response["fields"],
        "public_url": s3_response["public_url"]
    }


@router.delete("/{file_key:path}", response_model=FileDeleteResponse)
async def delete_file(
        file_key: str,
        owner_id: str,
        repo: MediaRepository = Depends(get_media_repo),
):
    file = await repo.get_by_key(file_key)
    if not file or str(file.owner_id) != owner_id:
        raise HTTPException(404, detail="File not found or access denied")

    if not s3.delete_object(file_key):
        raise HTTPException(500, detail="Failed to delete from storage")

    await repo.delete(file_key)

    return FileDeleteResponse(status="success", message="File deleted")
