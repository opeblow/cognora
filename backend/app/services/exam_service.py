import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.exam import ExamRepository, ExamResultRepository
from app.models.exam import ExamAnswer


class ExamService:
    def __init__(self, db: Session):
        self.exam_repo = ExamRepository(db)
        self.exam_result_repo = ExamResultRepository(db)
        self.db = db

    def get_exams(self, subject_id: str = None, exam_type: str = None, skip: int = 0, limit: int = 20) -> dict:
        filters = {}
        if subject_id:
            filters["subject_id"] = subject_id
        if exam_type:
            filters["exam_type"] = exam_type
        exams, total = self.exam_repo.get_all(skip=skip, limit=limit, **filters)
        return {
            "exams": [
                {
                    "id": str(e.id),
                    "subject_id": str(e.subject_id),
                    "title": e.title,
                    "description": e.description,
                    "exam_type": e.exam_type,
                    "year": e.year,
                    "time_limit_minutes": e.time_limit_minutes,
                    "total_questions": e.total_questions,
                    "pass_percentage": e.pass_percentage,
                }
                for e in exams
            ],
            "total": total,
        }

    def start_exam(self, exam_id: str, user_id: str) -> dict:
        exam = self.exam_repo.get_with_questions(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        in_progress = self.exam_result_repo.get_in_progress(user_id, exam_id)
        if in_progress:
            result_id = str(in_progress.id)
        else:
            result = self.exam_result_repo.create(
                exam_id=exam.id,
                user_id=user_id,
            )
            result_id = str(result.id)

        return {
            "result_id": result_id,
            "exam": {
                "id": str(exam.id),
                "title": exam.title,
                "description": exam.description,
                "exam_type": exam.exam_type,
                "year": exam.year,
                "time_limit_minutes": exam.time_limit_minutes,
                "pass_percentage": exam.pass_percentage,
                "questions": [
                    {
                        "id": str(q.id),
                        "text": q.text,
                        "options": q.options if isinstance(q.options, list) else json.loads(q.options),
                        "order_index": q.order_index,
                    }
                    for q in exam.questions
                ],
            },
            "time_limit_minutes": int(exam.time_limit_minutes or "0"),
        }

    def submit_exam(self, result_id: str, user_id: str, answers: dict, time_taken_seconds: int) -> dict:
        result = self.exam_result_repo.get(result_id)
        if not result or str(result.user_id) != user_id:
            raise ValueError("Exam result not found")

        if result.status != "in_progress":
            raise ValueError("Exam already completed")

        exam = self.exam_repo.get_with_questions(result.exam_id)
        if not exam:
            raise ValueError("Exam not found")

        questions = exam.questions
        total = len(questions)
        score = 0
        answer_details = []

        for question in questions:
            selected = answers.get(str(question.id))
            is_correct = selected == question.correct_answer
            if is_correct:
                score += 1

            answer = ExamAnswer(
                result_id=result.id,
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
        pass_percentage = int(exam.pass_percentage or 40)

        result.score = str(score)
        result.total = str(total)
        result.percentage = str(round(percentage, 2))
        result.time_taken_seconds = str(time_taken_seconds)
        result.status = "completed" if percentage >= pass_percentage else "failed"
        result.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        return {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "passed": percentage >= pass_percentage,
            "status": result.status,
            "answers": answer_details,
        }

    def get_results(self, user_id: str) -> dict:
        results = self.exam_result_repo.get_by_user(user_id)
        return {
            "results": [
                {
                    "id": str(r.id),
                    "exam_id": str(r.exam_id),
                    "score": r.score,
                    "total": r.total,
                    "percentage": r.percentage,
                    "time_taken_seconds": r.time_taken_seconds,
                    "status": r.status,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                }
                for r in results
            ],
            "total": len(results),
        }
