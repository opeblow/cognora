from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.past_question_service import PastQuestionService

router = APIRouter(prefix="/past-questions", tags=["Past Questions"])


class StartPracticeRequest(BaseModel):
    board: str
    subject: str
    year: int
    count: int = 20


class SubmitPracticeRequest(BaseModel):
    questions: list[dict]
    answers: dict


@router.get("/filters")
def get_filter_options(
    current_user: User = Depends(get_current_user),
):
    service = PastQuestionService()
    return service.get_filter_options()


@router.get("/subjects/{board}")
def get_subjects(
    board: str,
    current_user: User = Depends(get_current_user),
):
    service = PastQuestionService()
    subjects = service.get_subjects_for_board(board.upper())
    return {"subjects": subjects}


@router.get("/years/{board}")
def get_years(
    board: str,
    current_user: User = Depends(get_current_user),
):
    service = PastQuestionService()
    years = service.get_years_for_board(board.upper())
    return {"years": years}


@router.post("/start")
def start_practice(
    request: StartPracticeRequest,
    current_user: User = Depends(get_current_user),
):
    service = PastQuestionService()
    try:
        result = service.start_practice(
            board=request.board.upper(),
            subject=request.subject,
            year=request.year,
            count=request.count,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")


@router.post("/submit")
def submit_practice(
    request: SubmitPracticeRequest,
    current_user: User = Depends(get_current_user),
):
    if not request.questions:
        raise HTTPException(status_code=400, detail="No questions provided")
    if not request.answers:
        raise HTTPException(status_code=400, detail="No answers provided")
    service = PastQuestionService()
    return service.submit_practice(request.questions, request.answers)
