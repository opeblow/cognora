from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.content_issue import ContentIssue
from app.workers.tasks import review_content_issue
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/issues", tags=["Issues"])


class CreateIssueRequest(BaseModel):
    content_type: str
    content_id: str
    section_index: Optional[int] = None
    severity: str
    description: str


@router.post("", status_code=status.HTTP_201_CREATED)
def create_issue(
    request: CreateIssueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    issue = ContentIssue(
        user_id=str(current_user.id),
        content_type=request.content_type,
        content_id=request.content_id,
        section_index=request.section_index,
        severity=request.severity,
        description=request.description,
        status="open",
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    review_content_issue.delay(str(issue.id))

    return {
        "id": str(issue.id),
        "status": "open",
        "message": "Issue reported. Our AI is reviewing it.",
    }


@router.get("")
def list_issues(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    issues = (
        db.query(ContentIssue)
        .filter(ContentIssue.user_id == str(current_user.id))
        .order_by(ContentIssue.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "issues": [
            {
                "id": str(i.id),
                "content_type": i.content_type,
                "severity": i.severity,
                "description": i.description,
                "status": i.status,
                "ai_response": i.ai_response,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in issues
        ]
    }
