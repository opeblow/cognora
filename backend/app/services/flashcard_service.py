import json
import logging
import math
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.flashcard import Flashcard, FlashcardReview
from app.models.lesson import Topic
from app.core.config import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class FlashcardService:
    def __init__(self, db: Session):
        self.db = db
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=60.0) if settings.OPENAI_API_KEY else None

    def generate_flashcards(self, user_id: str, topic_id: str, count: int = 10) -> list[Flashcard]:
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise ValueError("Topic not found")

        if not self.openai:
            raise ValueError("OpenAI API key not configured")

        existing_tags = topic.title or ""

        response = self.openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a flashcard generator for Nigerian secondary school students "
                        "(WAEC/NECO/JAMB). Extract key concepts as Q&A pairs."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate {count} high-quality flashcards from this topic: {topic.title}\n\n"
                        f"Topic content:\n{topic.content or 'No content available'}\n\n"
                        "Each flashcard must have:\n"
                        "- question: A clear, specific question\n"
                        "- answer: A concise but complete answer\n"
                        "- difficulty: 'easy', 'medium', or 'hard'\n\n"
                        "Return ONLY valid JSON array:\n"
                        '[{"question": "...", "answer": "...", "difficulty": "medium"}]'
                    ),
                },
            ],
            temperature=0.5,
            max_tokens=4000,
        )

        text = response.choices[0].message.content or "[]"
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])

        try:
            pairs = json.loads(text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse flashcard JSON: {text[:200]}")
            raise ValueError("Failed to generate flashcards")

        flashcards = []
        for pair in pairs[:count]:
            card = Flashcard(
                user_id=user_id,
                topic_id=topic_id,
                question=pair.get("question", ""),
                answer=pair.get("answer", ""),
                difficulty=pair.get("difficulty", "medium"),
                source="ai_generated",
                is_active=True,
            )
            self.db.add(card)
            self.db.flush()

            review = FlashcardReview(
                flashcard_id=card.id,
                ease_factor=2.5,
                interval_days=0,
                repetitions=0,
            )
            self.db.add(review)
            self.db.flush()

            flashcards.append(card)

        self.db.commit()
        for card in flashcards:
            self.db.refresh(card)

        logger.info(f"Generated {len(flashcards)} flashcards for topic {topic_id}")
        return flashcards

    def get_flashcards(
        self, user_id: str, topic_id: Optional[str] = None,
        due_only: bool = False, skip: int = 0, limit: int = 50,
    ) -> tuple[list[dict], int]:
        query = self.db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.is_active == True,
        )

        if topic_id:
            query = query.filter(Flashcard.topic_id == topic_id)

        total = query.count()
        flashcards = query.offset(skip).limit(limit).all()

        now = datetime.now(timezone.utc)
        result = []
        for card in flashcards:
            review = card.review
            next_review = review.next_review_at if review else None
            if next_review is not None and next_review.tzinfo is None:
                next_review = next_review.replace(tzinfo=timezone.utc)
            due = next_review is None or next_review <= now

            if due_only and not due:
                continue

            result.append({
                "id": card.id,
                "question": card.question,
                "answer": card.answer,
                "difficulty": card.difficulty,
                "tags": card.tags,
                "topic_id": card.topic_id,
                "section_index": card.section_index,
                "next_review_at": next_review,
                "ease_factor": review.ease_factor if review else 2.5,
                "interval_days": review.interval_days if review else 0,
                "repetitions": review.repetitions if review else 0,
                "due": due,
            })

        return result, total

    def review_flashcard(self, flashcard_id: str, user_id: str, quality: int) -> dict:
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")

        card = self.db.query(Flashcard).filter(
            Flashcard.id == flashcard_id,
            Flashcard.user_id == user_id,
        ).first()
        if not card:
            raise ValueError("Flashcard not found")

        if not card.review:
            review = FlashcardReview(
                flashcard_id=card.id,
                ease_factor=2.5,
                interval_days=0,
                repetitions=0,
            )
            self.db.add(review)
            self.db.flush()
        else:
            review = card.review

        ef = review.ease_factor or 2.5
        interval = review.interval_days or 0
        reps = review.repetitions or 0

        ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        if quality < 3:
            interval = 1
            reps = 0
        elif reps == 0:
            interval = 1
            reps = 1
        elif reps == 1:
            interval = 6
            reps = 2
        else:
            interval = round(interval * ef)
            reps += 1

        now = datetime.now(timezone.utc)
        review.ease_factor = round(ef, 2)
        review.interval_days = interval
        review.repetitions = reps
        review.next_review_at = now + timedelta(days=interval)
        review.last_reviewed_at = now

        self.db.commit()
        self.db.refresh(review)

        return {
            "id": card.id,
            "next_review_at": review.next_review_at,
            "interval_days": interval,
            "ease_factor": round(ef, 2),
            "repetitions": reps,
        }

    def create_flashcard_manually(
        self, user_id: str, question: str, answer: str,
        topic_id: Optional[str] = None, difficulty: str = "medium",
        tags: Optional[str] = None,
    ) -> Flashcard:
        card = Flashcard(
            user_id=user_id,
            topic_id=topic_id,
            question=question,
            answer=answer,
            difficulty=difficulty,
            tags=tags,
            source="manual",
            is_active=True,
        )
        self.db.add(card)
        self.db.flush()

        review = FlashcardReview(
            flashcard_id=card.id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(card)
        return card

    def delete_flashcard(self, flashcard_id: str, user_id: str) -> bool:
        card = self.db.query(Flashcard).filter(
            Flashcard.id == flashcard_id,
            Flashcard.user_id == user_id,
        ).first()
        if not card:
            return False
        card.is_active = False
        self.db.commit()
        return True
