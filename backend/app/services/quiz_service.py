import json
import random
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.quiz import QuizRepository, QuizAttemptRepository
from app.repositories.subject import SubjectRepository
from app.models.quiz import QuizAnswer
from app.models.lesson import Topic
from app.services.question_pool_service import QuestionPoolService
from typing import Optional


class QuizService:
    def __init__(self, db: Session):
        self.quiz_repo = QuizRepository(db)
        self.quiz_attempt_repo = QuizAttemptRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.pool_service = QuestionPoolService(db)
        self.db = db

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

    def get_quiz_detail(self, quiz_id: str, user_id: str) -> dict:
        quiz = self.quiz_repo.get_with_questions(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        hardcoded = list(quiz.questions)
        target_count = 15
        subject_id = str(quiz.subject_id)

        topics = [
            t.title for t in self.db.query(Topic)
            .join(Topic.lesson)
            .filter(Topic.lesson.has(subject_id=subject_id))
            .all()
        ]

        pool_questions = self.pool_service.get_questions_for_quiz(
            subject_id=subject_id,
            user_id=user_id,
            num_questions=target_count,
            topics=topics,
            mark_seen=False,
        )

        all_questions = hardcoded + pool_questions
        random.shuffle(all_questions)
        selected = all_questions[:target_count]

        return {
            "id": str(quiz.id),
            "title": quiz.title,
            "description": quiz.description,
            "difficulty": quiz.difficulty,
            "time_limit_minutes": quiz.time_limit_minutes,
            "pass_percentage": quiz.pass_percentage,
            "questions": [
                {
                    "id": str(q.id),
                    "text": q.text,
                    "options": q.options if isinstance(q.options, list) else json.loads(q.options) if isinstance(q.options, str) else q.options,
                    "order_index": i + 1,
                    "question_type": getattr(q, 'question_type', 'multiple_choice'),
                }
                for i, q in enumerate(selected)
            ],
            "question_count": len(selected),
        }

    def submit_quiz(self, quiz_id: str, user_id: str, answers: dict, time_taken_seconds: int) -> dict:
        quiz = self.quiz_repo.get_with_questions(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        hardcoded = list(quiz.questions)
        subject_id = str(quiz.subject_id)

        topics = [
            t.title for t in self.db.query(Topic)
            .join(Topic.lesson)
            .filter(Topic.lesson.has(subject_id=subject_id))
            .all()
        ]

        pool_questions = self.pool_service.get_questions_for_quiz(
            subject_id=subject_id,
            user_id=user_id,
            num_questions=15,
            topics=topics,
            mark_seen=True,
        )

        all_questions = hardcoded + pool_questions
        total = len(all_questions)
        score = 0
        answer_details = []

        attempt = self.quiz_attempt_repo.create(
            quiz_id=quiz.id,
            user_id=user_id,
            time_taken_seconds=str(time_taken_seconds),
        )

        for question in all_questions:
            qid = str(question.id)
            selected = answers.get(qid)
            is_correct = selected == question.correct_answer
            if is_correct:
                score += 1

            is_pool = hasattr(question, 'source') and question.source == 'ai_generated'
            answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=None if is_pool else question.id,
                pool_question_id=question.id if is_pool else None,
                selected_answer=selected or "",
                is_correct=is_correct,
            )
            self.db.add(answer)

            answer_details.append({
                "question_id": qid,
                "question_text": question.text,
                "selected_answer": selected,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
            })

        percentage = (score / total * 100) if total > 0 else 0
        pass_percentage = int(quiz.pass_percentage or 50)

        attempt.score = str(score)
        attempt.total = str(total)
        attempt.percentage = str(round(percentage, 2))
        attempt.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        try:
            from app.services.analytics_service import AnalyticsService
            analytics = AnalyticsService(self.db)
            analytics.log_event(
                user_id=user_id,
                event_type="quiz_completed",
                event_data={
                    "quiz_id": quiz_id,
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
                review_suggestion = planner.check_and_suggest_reviews(user_id, str(attempt.id))
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
        attempts = self.quiz_attempt_repo.get_by_user(user_id)
        return {
            "attempts": [
                {
                    "id": str(a.id),
                    "quiz_id": str(a.quiz_id),
                    "score": a.score,
                    "total": a.total,
                    "percentage": a.percentage,
                    "time_taken_seconds": a.time_taken_seconds,
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                }
                for a in attempts
            ],
            "total": len(attempts),
        }
