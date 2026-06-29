from pydantic import BaseModel, ConfigDict
from typing import Optional, Any


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

