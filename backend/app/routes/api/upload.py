from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.file_storage_service import FileUploadService
from app.schemas.file import UploadFileResponse, FileListResponse, OcrStatusResponse

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=UploadFileResponse)
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    service = FileUploadService(db)
    try:
        record = service.store_file(
            user_id=str(current_user.id),
            file=file.file,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            file_size=file.size or 0,
        )
        return UploadFileResponse(
            id=record.id,
            original_filename=record.original_filename,
            mime_type=record.mime_type,
            file_size=record.file_size,
            ocr_status=record.ocr_status,
            created_at=record.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=FileListResponse)
def list_files(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FileUploadService(db)
    files, total = service.get_user_files(str(current_user.id), skip, limit)
    return FileListResponse(
        files=[
            UploadFileResponse(
                id=f.id,
                original_filename=f.original_filename,
                mime_type=f.mime_type,
                file_size=f.file_size,
                ocr_status=f.ocr_status,
                created_at=f.created_at,
            )
            for f in files
        ],
        total=total,
    )


@router.get("/{file_id}/ocr-status", response_model=OcrStatusResponse)
def get_ocr_status(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FileUploadService(db)
    record = service.get_file(file_id, str(current_user.id))
    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    return OcrStatusResponse(
        id=record.id,
        ocr_status=record.ocr_status,
        ocr_text=record.ocr_text,
        ocr_processed_at=record.ocr_processed_at,
    )
