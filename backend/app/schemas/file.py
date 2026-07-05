from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    id: str
    original_filename: str
    mime_type: str
    file_size: int
    ocr_status: str
    created_at: datetime


class FileListResponse(BaseModel):
    files: list[UploadFileResponse]
    total: int


class OcrStatusResponse(BaseModel):
    id: str
    ocr_status: str
    ocr_text: Optional[str] = None
    ocr_processed_at: Optional[datetime] = None
