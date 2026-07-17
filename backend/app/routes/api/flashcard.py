from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.flashcard_service import FlashcardService
from app.schemas.flashcard import (
    FlashcardResponse,
    FlashcardListResponse,
    ReviewFlashcardRequest,
    ReviewFlashcardResponse,
    GenerateFlashcardsRequest,
)

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


def _card_to_response(card: dict) -> FlashcardResponse:
    return FlashcardResponse(
        id=card["id"],
        question=card["question"],
        answer=card["answer"],
        difficulty=card.get("difficulty"),
        tags=card.get("tags"),
        topic_id=card.get("topic_id"),
        section_index=card.get("section_index"),
        next_review_at=card.get("next_review_at"),
        ease_factor=card.get("ease_factor", 2.5),
        interval_days=card.get("interval_days", 0),
        repetitions=card.get("repetitions", 0),
    )


@router.get("", response_model=FlashcardListResponse)
def get_flashcards(
    topic_id: str = Query(None),
    due_only: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FlashcardService(db)
    cards, total = service.get_flashcards(
        user_id=str(current_user.id),
        topic_id=topic_id,
        due_only=due_only,
        skip=skip,
        limit=limit,
    )
    return FlashcardListResponse(
        flashcards=[_card_to_response(c) for c in cards],
        total=total,
    )


@router.post("/generate", response_model=FlashcardListResponse)
def generate_flashcards(
    request: GenerateFlashcardsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FlashcardService(db)
    try:
        cards = service.generate_flashcards(
            user_id=str(current_user.id),
            topic_id=request.topic_id,
            count=request.count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result, total = service.get_flashcards(
        user_id=str(current_user.id),
        topic_id=request.topic_id,
    )
    return FlashcardListResponse(
        flashcards=[_card_to_response(c) for c in result],
        total=total,
    )


@router.post("/{flashcard_id}/review", response_model=ReviewFlashcardResponse)
def review_flashcard(
    flashcard_id: str,
    request: ReviewFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FlashcardService(db)
    try:
        result = service.review_flashcard(
            flashcard_id=flashcard_id,
            user_id=str(current_user.id),
            quality=request.quality,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ReviewFlashcardResponse(**result)


@router.delete("/{flashcard_id}", response_model=dict)
def delete_flashcard(
    flashcard_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FlashcardService(db)
    deleted = service.delete_flashcard(flashcard_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return {"message": "Flashcard deleted"}


@router.delete("", response_model=dict)
def delete_all_flashcards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FlashcardService(db)
    count = service.delete_all_flashcards(str(current_user.id))
    return {"message": f"Deleted {count} flashcards", "deleted": count}
