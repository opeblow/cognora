from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.schemas.exam import SubmitExamRequest
from app.services.exam_service import ExamService
from app.services.credit_service import CreditService
from app.models.user import User

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("", response_model=dict)
def get_exams(
    subject_id: str = None,
    exam_type: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    skip = (page - 1) * page_size
    return service.get_exams(subject_id, exam_type, skip, page_size)


@router.post("/{exam_id}/start", response_model=dict)
def start_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit_service = CreditService(db)
    try:
        credit_service.deduct_credits(str(current_user.id), "mock_exam")
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    service = ExamService(db)
    try:
        return service.start_exam(exam_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/results/{result_id}/submit", response_model=dict)
def submit_exam(
    result_id: str,
    request: SubmitExamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    try:
        return service.submit_exam(result_id, str(current_user.id), request.answers, request.time_taken_seconds)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/results/mine", response_model=dict)
def get_my_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    return service.get_results(str(current_user.id))
