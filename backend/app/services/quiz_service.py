import concurrent.futures
import json
import random
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.quiz import QuizRepository, QuizAttemptRepository
from app.repositories.subject import SubjectRepository
from app.models.lesson import Topic
from app.models.quiz_session import QuizSession
from app.services.ai_service import AIService
from typing import Optional

import re

def strip_tags(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)

_ai_semaphore = None


def _get_ai_semaphore():
    global _ai_semaphore
    if _ai_semaphore is None:
        _ai_semaphore = __import__("asyncio").Semaphore(4)
    return _ai_semaphore


class QuizService:
    def __init__(self, db: Session):
        self.quiz_repo = QuizRepository(db)
        self.quiz_attempt_repo = QuizAttemptRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.db = db
        self.ai_service = AIService()

    def get_quizzes(self, subject_id: Optional[str] = None, skip: int = 0, limit: int = 20) -> dict:
        filters = {}
        if subject_id:
            filters["subject_id"] = subject_id
        quizzes, total = self.quiz_repo.get_all(skip=skip, limit=limit, **filters)
        return {
            "quizzes": [
                {
                    "id": str(q.id),
                    "subject_id": str(q.subject_id),
                    "title": q.title,
                    "description": q.description,
                    "difficulty": q.difficulty,
                    "time_limit_minutes": q.time_limit_minutes,
                    "pass_percentage": q.pass_percentage,
                }
                for q in quizzes
            ],
            "total": total,
        }

    def _normalize_correct_answer(self, correct_answer: str, options: list[str]) -> str:
        """Map a letter answer (\"A\") to the full option text (\"A) Option A\")."""
        letter = correct_answer.strip().upper().rstrip(")")
        for opt in options:
            if opt.strip().upper().startswith(letter + ")"):
                return opt
        return correct_answer

    async def _generate_questions_for_session(self, subject_name: str, topics: list[str], count: int) -> list[dict]:
        """Generate questions via parallel AI calls with caching and concurrency control."""
        import asyncio
        if not topics:
            topics = ["general"]

        cache_key = f"quiz_questions:{subject_name}:{':'.join(sorted(topics))}"
        from app.database.redis import get_redis
        redis = await get_redis()
        
        cached_data = await redis.get(cache_key)
        if cached_data:
            try:
                cached = json.loads(cached_data)
                random.shuffle(cached)
                return cached[:count]
            except Exception:
                pass


        BATCH_SIZE = 10
        num_batches = 1
        all_questions = []
        seen_texts: set[str] = set()
        sem = _get_ai_semaphore()

        async def _gen_batch(batch_idx: int) -> list[dict]:
            topic = topics[batch_idx % len(topics)]
            async with sem:
                try:
                    return await self.ai_service.generate_exam_questions_for_topic(
                        subject=subject_name,
                        exam_type="WAEC/JAMB",
                        topic=topic,
                        num_questions=BATCH_SIZE,
                        skip_search=False
                    )
                except Exception:
                    return []

        results = await asyncio.gather(*[_gen_batch(i) for i in range(num_batches)])
        for batch_result in results:
            for q_data in batch_result:
                text = (q_data.get("text") or "").strip()
                options = q_data.get("options", [])
                correct = q_data.get("correct_answer", "")

                if not text or len(text) < 15 or not options or len(options) < 2 or not correct:
                    continue
                text_lower = text.lower()
                if text_lower in seen_texts or "first question" in text_lower:
                    continue
                seen_texts.add(text_lower)

                all_questions.append({
                    "id": str(uuid.uuid4()),
                    "text": strip_tags(text),
                    "options": [strip_tags(opt) for opt in options],
                    "correct_answer": strip_tags(self._normalize_correct_answer(correct, options)),
                    "explanation": strip_tags(q_data.get("explanation", "")),
                    "difficulty": q_data.get("difficulty", "hard"),
                    "question_type": "multiple_choice",
                })

        if all_questions:
            await redis.setex(cache_key, 3600, json.dumps(all_questions))


        random.shuffle(all_questions)
        return all_questions[:count]

    async def get_quiz_detail(self, quiz_id: str, user_id: str) -> dict:
        quiz = self.quiz_repo.get_with_questions(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        target_count = 10
        subject_id = str(quiz.subject_id)
        subject = self.subject_repo.get(subject_id)

        topics = [
            t.title for t in self.db.query(Topic)
            .join(Topic.lesson)
            .filter(Topic.lesson.has(subject_id=subject_id))
            .all()
        ]

        raw_questions = await self._generate_questions_for_session(
            subject_name=subject.name if subject else "",
            topics=topics,
            count=target_count,
        )

        random.shuffle(raw_questions)
        selected = raw_questions[:target_count]

        for i, q in enumerate(selected):
            q["order_index"] = i + 1

        session = QuizSession(
            quiz_id=quiz.id,
            user_id=user_id,
            questions_data=[
                {
                    "id": q["id"],
                    "text": q["text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q.get("explanation", ""),
                    "order_index": q["order_index"],
                    "question_type": q.get("question_type", "multiple_choice"),
                }
                for q in selected
            ],
            status="in_progress",
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return {
            "id": str(quiz.id),
            "title": quiz.title,
            "description": quiz.description,
            "difficulty": quiz.difficulty,
            "time_limit_minutes": quiz.time_limit_minutes,
            "pass_percentage": quiz.pass_percentage,
            "session_id": str(session.id),
            "question_count": len(selected),
            "questions": [
                {
                    "id": q["id"],
                    "text": q["text"],
                    "options": q["options"],
                    "order_index": q["order_index"],
                    "question_type": q.get("question_type", "multiple_choice"),
                }
                for q in selected
            ],
        }

    def submit_quiz(self, session_id: str, user_id: str, answers: dict, time_taken_seconds: int) -> dict:
        session = self.db.query(QuizSession).filter(
            QuizSession.id == session_id,
            QuizSession.user_id == user_id,
        ).first()

        if not session:
            raise ValueError("Quiz session not found. Please start the quiz again.")

        if session.status == "completed":
            raise ValueError("This quiz has already been submitted.")

        questions_data = session.questions_data or []
        total = len(questions_data)
        score = 0
        answer_details = []

        for q_data in questions_data:
            qid = q_data.get("id", "")
            correct_answer = q_data.get("correct_answer", "")
            question_text = q_data.get("text", "")

            selected = answers.get(qid) or ""
            correct_letter = correct_answer.strip().upper().rstrip(")")
            selected_letter = selected.strip().upper().rstrip(")")
            is_correct = selected_letter == correct_letter
            if is_correct:
                score += 1

            answer_details.append({
                "question_id": qid,
                "question_text": question_text,
                "selected_answer": selected,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": q_data.get("explanation", ""),
            })

        percentage = (score / total * 100) if total > 0 else 0
        quiz = session.quiz
        pass_percentage = int(quiz.pass_percentage or 50) if quiz else 50

        session.score = score
        session.total = total
        session.percentage = round(percentage)
        session.time_taken_seconds = time_taken_seconds
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        try:
            from app.services.analytics_service import AnalyticsService
            analytics = AnalyticsService(self.db)
            analytics.log_event(
                user_id=user_id,
                event_type="quiz_completed",
                event_data={
                    "quiz_id": session.quiz_id,
                    "score": score,
                    "total": total,
                    "percentage": round(percentage, 2),
                    "passed": percentage >= pass_percentage,
                },
            )
        except Exception:
            pass

        try:
            from app.services.gamification_service import GamificationService
            from app.repositories.user import UserRepository
            user_repo = UserRepository(self.db)
            user = user_repo.get(user_id)
            if user:
                gs = GamificationService(self.db)
                gs.update_streak(user)
                xp_earned = round(10 * (percentage / 100))
                gs.add_xp(user, max(1, xp_earned), reason="quiz_completed")
        except Exception:
            pass

        review_suggestion = None
        if percentage < 60 and score < total:
            try:
                from app.services.study_plan_service import StudyPlanService
                planner = StudyPlanService(self.db)
                review_suggestion = planner.check_and_suggest_reviews(user_id, str(session.id))
            except Exception:
                pass

        return {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "passed": percentage >= pass_percentage,
            "answers": answer_details,
            "review_suggestion": review_suggestion,
        }

    def get_attempts(self, user_id: str) -> dict:
        sessions = self.db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.status == "completed",
        ).order_by(QuizSession.completed_at.desc()).all()

        return {
            "attempts": [
                {
                    "id": str(s.id),
                    "quiz_id": str(s.quiz_id),
                    "score": str(s.score) if s.score is not None else None,
                    "total": str(s.total) if s.total is not None else None,
                    "percentage": str(s.percentage) if s.percentage is not None else None,
                    "time_taken_seconds": str(s.time_taken_seconds) if s.time_taken_seconds is not None else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ],
            "total": len(sessions),
        }
