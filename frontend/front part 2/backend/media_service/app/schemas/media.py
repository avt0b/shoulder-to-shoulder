from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    purpose: str
    content_type: str = Field(..., pattern=r"^image/(jpeg|png|webp)$")
    file_size: int = Field(..., le=10_485_760)  # Макс 10МБ
    owner_id: str


class FileDeleteResponse(BaseModel):
    status: str
    message: str
