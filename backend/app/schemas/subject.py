from pydantic import BaseModel, ConfigDict
from typing import Optional


class SubjectResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    category: str
    icon: Optional[str] = None
    color: Optional[str] = None

    


class SubjectListResponse(BaseModel):
    subjects: list[SubjectResponse]
    total: int

