import os
import uuid
import shutil
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import BinaryIO
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    @abstractmethod
    def save(self, file: BinaryIO, filename: str) -> tuple[str, str]:
        ...

    @abstractmethod
    def get_path(self, stored_name: str) -> str:
        ...

    @abstractmethod
    def delete(self, stored_name: str) -> bool:
        ...


class LocalStorageBackend(StorageBackend):
    def __init__(self):
        self.base_dir = Path(settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file: BinaryIO, filename: str) -> tuple[str, str]:
        ext = Path(filename).suffix or ""
        stored_name = f"{uuid.uuid4().hex}{ext}"
        dest = self.base_dir / stored_name
        with open(dest, "wb") as f:
            shutil.copyfileobj(file, f)
        return stored_name, str(dest)

    def get_path(self, stored_name: str) -> str:
        return str(self.base_dir / stored_name)

    def delete(self, stored_name: str) -> bool:
        path = self.base_dir / stored_name
        if path.exists():
            path.unlink()
            return True
        return False


class FileUploadService:
    def __init__(self, db):
        self.db = db
        self.storage = LocalStorageBackend()
        self.max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        self.allowed_types = settings.ALLOWED_UPLOAD_TYPES

    def validate_file(self, filename: str, file_size: int, mime_type: str) -> None:
        if file_size > self.max_size:
            raise ValueError(
                f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        if mime_type not in self.allowed_types:
            raise ValueError(
                f"File type '{mime_type}' is not allowed. "
                f"Allowed types: {', '.join(self.allowed_types)}"
            )

    def store_file(
        self, user_id: str, file: BinaryIO, filename: str, mime_type: str, file_size: int
    ):
        from app.models.uploaded_file import UploadedFile

        self.validate_file(filename, file_size, mime_type)
        stored_name, storage_path = self.storage.save(file, filename)

        record = UploadedFile(
            user_id=user_id,
            original_filename=filename,
            stored_filename=stored_name,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            storage_backend="local",
            ocr_status="pending",
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_file(self, file_id: str, user_id: str | None = None):
        from app.models.uploaded_file import UploadedFile

        query = self.db.query(UploadedFile).filter(UploadedFile.id == file_id)
        if user_id is not None:
            query = query.filter(UploadedFile.user_id == user_id)
        return query.first()

    def get_file_by_id(self, file_id: str):
        from app.models.uploaded_file import UploadedFile

        return self.db.query(UploadedFile).filter(
            UploadedFile.id == file_id
        ).first()

    def get_user_files(self, user_id: str, skip: int = 0, limit: int = 50):
        from app.models.uploaded_file import UploadedFile

        query = self.db.query(UploadedFile).filter(
            UploadedFile.user_id == user_id
        ).order_by(UploadedFile.created_at.desc())

        total = query.count()
        files = query.offset(skip).limit(limit).all()
        return files, total

    def update_ocr_status(self, file_id: str, status: str, ocr_text: str = None):
        from app.models.uploaded_file import UploadedFile
        from datetime import datetime, timezone

        record = self.db.query(UploadedFile).filter(
            UploadedFile.id == file_id
        ).first()
        if not record:
            return None

        record.ocr_status = status
        if ocr_text is not None:
            record.ocr_text = ocr_text
        if status in ("completed", "failed"):
            record.ocr_processed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record
