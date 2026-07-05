from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    id: str
    processing_status: str
    message: str


class AudioTranscriptionResponse(BaseModel):
    id: str
    transcript: Optional[str] = None
    ai_feedback: Optional[str] = None
    processing_status: str
