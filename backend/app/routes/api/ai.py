from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.schemas.ai import TutorRequest, TutorResponse, GenerateQuizRequest, GenerateQuizResponse
from app.services.ai_service import AIService
from app.services.credit_service import CreditService
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI Tutor"])


@router.post("/tutor", response_model=TutorResponse)
def tutor_chat(
    request: TutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit_service = CreditService(db)
    try:
        credit_service.deduct_credits(str(current_user.id), "ai_ask")
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    ai_service = AIService()
    result = ai_service.tutor_chat(request.message, request.subject, request.context)
    return TutorResponse(**result)


@router.post("/generate-quiz", response_model=dict)
def generate_quiz(
    request: GenerateQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit_service = CreditService(db)
    try:
        credit_service.deduct_credits(str(current_user.id), "generate_quiz")
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    ai_service = AIService()
    result = ai_service.generate_quiz(request.subject, request.topic, request.difficulty, request.num_questions)
    return result
