import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.quiz import QuizRepository, QuizAttemptRepository
from app.repositories.subject import SubjectRepository
from app.models.quiz import QuizAnswer
from typing import Optional


class QuizService:
    def __init__(self, db: Session):
        self.quiz_repo = QuizRepository(db)
        self.quiz_attempt_repo = QuizAttemptRepository(db)
        self.subject_repo = SubjectRepository(db)
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

    def get_quiz_detail(self, quiz_id: str) -> dict:
        quiz = self.quiz_repo.get_with_questions(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

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
                    "options": q.options if isinstance(q.options, list) else json.loads(q.options),
                    "order_index": q.order_index,
                    "question_type": q.question_type,
                }
                for q in quiz.questions
            ],
        }

    def submit_quiz(self, quiz_id: str, user_id: str, answers: dict, time_taken_seconds: int) -> dict:
        quiz = self.quiz_repo.get_with_questions(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        questions = quiz.questions
        total = len(questions)
        score = 0
        answer_details = []

        attempt = self.quiz_attempt_repo.create(
            quiz_id=quiz.id,
            user_id=user_id,
            time_taken_seconds=str(time_taken_seconds),
        )

        for question in questions:
            selected = answers.get(str(question.id))
            is_correct = selected == question.correct_answer
            if is_correct:
                score += 1

            answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_answer=selected or "",
                is_correct=is_correct,
            )
            self.db.add(answer)

            answer_details.append({
                "question_id": str(question.id),
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

        return {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "passed": percentage >= pass_percentage,
            "answers": answer_details,
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
