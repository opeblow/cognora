from pydantic import BaseModel
from typing import Optional


class CreateIssueRequest(BaseModel):
    content_type: str
    content_id: str
    section_index: Optional[int] = None
    severity: str
    description: str


class IssueResponse(BaseModel):
    id: str
    status: str
    message: str
