from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.repositories.subject import SubjectRepository
from app.models.user import User

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=dict)
def get_subjects(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = SubjectRepository(db)
    if category:
        subjects = repo.get_by_category(category)
    else:
        subjects, _ = repo.get_all()
    return {
        "subjects": [
            {
                "id": str(s.id),
                "name": s.name,
                "slug": s.slug,
                "description": s.description,
                "category": s.category,
                "icon": s.icon,
                "color": s.color,
            }
            for s in subjects
        ],
        "total": len(subjects),
    }


@router.get("/{slug}", response_model=dict)
def get_subject(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = SubjectRepository(db)
    subject = repo.get_by_slug(slug)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {
        "id": str(subject.id),
        "name": subject.name,
        "slug": subject.slug,
        "description": subject.description,
        "category": subject.category,
        "icon": subject.icon,
        "color": subject.color,
    }
