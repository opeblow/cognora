from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.schemas.exam import SubmitExamRequest
from app.services.exam_service import ExamService
from app.services.credit_service import CreditService
from app.services.ai_service import AIService
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

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
async def start_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    credit_service = CreditService(db)
    user_id = str(current_user.id)

    try:
        in_progress = service.exam_result_repo.get_in_progress(user_id, exam_id)
        is_new = in_progress is None

        if is_new:
            try:
                credit_service.deduct_credits(user_id, "mock_exam")
            except ValueError as e:
                raise HTTPException(status_code=402, detail=str(e))

        result = await service.start_exam_async(exam_id, user_id)

        if is_new and not result.get("is_new"):
            try:
                credit_service.add_credits(user_id, 10, description="Exam start failed — refund")
            except Exception:
                pass

        return result
    except HTTPException:
        raise
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


@router.post("/{exam_id}/generate-questions", response_model=dict)
async def generate_exam_questions(
    exam_id: str,
    num_questions: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Live questions were never included in the persisted attempt and therefore
    # could not be scored safely. Keep the route disabled until per-attempt
    # snapshots are introduced.
    raise HTTPException(status_code=410, detail="Live question generation is temporarily unavailable")
