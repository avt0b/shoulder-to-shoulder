import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.media_service.app.api.v1.dependencies import get_media_repo
from backend.media_service.app.core.config import settings
from backend.media_service.app.core.s3_client import s3
from backend.media_service.app.repositories.media_repository import MediaRepository
from backend.media_service.app.schemas.media import (
    FileDeleteResponse,
    MediaUploadResponse,
    UploadUrlRequest,
)

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/avatar/{owner_id}/{file_name:path}")
async def get_avatar(owner_id: str, file_name: str):
    file_key = f"avatar/{owner_id}/{file_name}"
    try:
        obj = s3.get_object(file_key)
    except Exception as e:
        raise HTTPException(404, detail=f"File not found: {e}")

    return StreamingResponse(
        obj["Body"].iter_chunks(),
        media_type=obj.get("ContentType") or "application/octet-stream",
    )


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_file(
    purpose: str = Form(...),
    owner_id: str = Form(...),
    file: UploadFile = File(...),
    repo: MediaRepository = Depends(get_media_repo),
):
    if purpose not in settings.ALLOWED_PURPOSES:
        raise HTTPException(400, detail="Invalid purpose")
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, detail="Invalid content type")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(413, detail="File is too large")

    ext = file.content_type.split("/")[-1]
    file_key = f"{purpose}/{owner_id}/{uuid.uuid4().hex[:10]}.{ext}"

    try:
        s3.upload_fileobj(file.file, file_key, file.content_type)
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to upload file: {e}")

    public_url = s3.get_public_url(file_key)
    await repo.create_uploaded_file(
        {
            "file_key": file_key,
            "owner_id": owner_id,
            "purpose": purpose,
            "content_type": file.content_type,
            "file_size": file_size,
            "public_url": public_url,
        }
    )

    return {"file_key": file_key, "public_url": public_url}


@router.post("/upload-url")
async def get_upload_url(
    req: UploadUrlRequest,
    repo: MediaRepository = Depends(get_media_repo),
):
    if req.purpose not in settings.ALLOWED_PURPOSES:
        raise HTTPException(400, detail="Invalid purpose")
    if req.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, detail="Invalid content type")
    if req.file_size <= 0:
        raise HTTPException(400, detail="Invalid file size")
    if req.file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(413, detail="File is too large")

    ext = req.content_type.split("/")[-1]
    file_key = f"{req.purpose}/{req.owner_id}/{uuid.uuid4().hex[:10]}.{ext}"
    s3_response = s3.generate_upload_url(file_key, req.content_type)

    await repo.create_pending_file(
        {
            "file_key": file_key,
            "owner_id": req.owner_id,
            "purpose": req.purpose,
            "content_type": req.content_type,
            "file_size": req.file_size,
            "public_url": s3_response["public_url"],
        }
    )

    return {
        "file_key": file_key,
        "upload_url": s3_response["upload_url"],
        "fields": s3_response["fields"],
        "public_url": s3_response["public_url"],
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
