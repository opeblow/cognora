from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.schemas.quiz import SubmitQuizRequest
from app.services.quiz_service import QuizService
from app.models.user import User

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("", response_model=dict)
def get_quizzes(
    subject_id: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = QuizService(db)
    skip = (page - 1) * page_size
    return service.get_quizzes(subject_id, skip, page_size)


@router.get("/{quiz_id}", response_model=dict)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = QuizService(db)
    try:
        return await service.get_quiz_detail(quiz_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{quiz_id}/submit", response_model=dict)
def submit_quiz(
    quiz_id: str,
    request: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = QuizService(db)
    try:
        return service.submit_quiz(request.session_id, str(current_user.id), request.answers, request.time_taken_seconds)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/attempts/mine", response_model=dict)
def get_my_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = QuizService(db)
    return service.get_attempts(str(current_user.id))
