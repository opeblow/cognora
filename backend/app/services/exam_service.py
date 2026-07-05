import json
import random
import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.exam import ExamRepository, ExamResultRepository
from app.models.exam import ExamAnswer, ExamQuestion
from app.models.subject import Subject
from app.models.lesson import Topic, Lesson
from app.services.question_pool_service import QuestionPoolService
from app.services.ai_service import AIService
from app.utils.exam_standards import EXAM_TYPE_STANDARDS, JAMB_STANDARDS


class ExamService:
    def __init__(self, db: Session):
        self.exam_repo = ExamRepository(db)
        self.exam_result_repo = ExamResultRepository(db)
        self.pool_service = QuestionPoolService(db)
        self.ai_service = AIService()
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

    def _make_seed(self, user_id: str, exam_id: str, salt: str = "") -> int:
        """Create a deterministic but unique shuffle seed per user + exam."""
        raw = f"{user_id}:{exam_id}:{salt}:{datetime.now(timezone.utc).isoformat()[:16]}"
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return int(digest[:12], 16)

    def _shuffle_questions(self, questions: list, user_id: str, exam_id: str) -> list:
        """Shuffle questions using a user-exam seeded RNG for unique ordering per user."""
        seed = self._make_seed(user_id, exam_id, "shuffle")
        rng = random.Random(seed)
        shuffled = list(questions)
        rng.shuffle(shuffled)
        return shuffled

    def _shuffle_options(self, questions: list, user_id: str, exam_id: str) -> list:
        """Shuffle option order within each question for additional uniqueness."""
        seed = self._make_seed(user_id, exam_id, "options")
        rng = random.Random(seed)
        for q in questions:
            options = q.options if isinstance(q.options, list) else json.loads(q.options)
            correct = q.correct_answer
            correct_letter = correct.strip().upper()

            option_pairs = []
            for opt in options:
                opt = opt.strip()
                if opt and len(opt) > 2 and opt[1] == ")":
                    letter = opt[0].upper()
                    text = opt[2:].strip()
                    option_pairs.append((letter, text))

            if len(option_pairs) == 4:
                rng.shuffle(option_pairs)
                new_labels = ["A", "B", "C", "D"]
                new_options = [f"{nl}) {text}" for nl, (_, text) in zip(new_labels, option_pairs)]

                label_map = {}
                for old_letter, new_letter in zip([p[0] for p in option_pairs], new_labels):
                    label_map[old_letter] = new_letter

                if correct_letter in label_map:
                    q.correct_answer = label_map[correct_letter]

                q.options = new_options

        return questions

    async def start_exam_async(self, exam_id: str, user_id: str) -> dict:
        """Async version with live question generation via Brave API."""
        exam = self.exam_repo.get_with_questions(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        in_progress = self.exam_result_repo.get_in_progress(user_id, exam_id)
        if in_progress:
            result_id = str(in_progress.id)
            questions = self._get_existing_questions(exam, result_id)
            is_new = False
        else:
            standards = EXAM_TYPE_STANDARDS.get(exam.exam_type, JAMB_STANDARDS)
            subject_standard = standards.get(exam.subject.slug, {"questions": 50, "minutes": 60})
            target_count = exam.total_questions or subject_standard["questions"] or 50
            time_limit = exam.time_limit_minutes or subject_standard["minutes"] or 60

            existing_qs = list(exam.questions) if exam.questions else []
            questions = list(existing_qs)

            if len(questions) < target_count:
                needed = target_count - len(questions)
                try:
                    live_qs = await self._fetch_live_questions(exam, user_id, needed)
                    for lq in live_qs:
                        eq = ExamQuestion(
                            exam_id=exam.id,
                            text=lq["text"],
                            options=lq["options"],
                            correct_answer=lq["correct_answer"],
                            explanation=lq.get("explanation", ""),
                            order_index=len(questions) + 1,
                        )
                        self.db.add(eq)
                        self.db.flush()
                        questions.append(eq)
                except Exception as e:
                    logger = __import__("logging").getLogger(__name__)
                    logger.warning(f"Live question fetch failed, using pool: {e}")
                    pool_questions = self.pool_service.get_questions_for_exam(
                        subject_id=str(exam.subject_id),
                        user_id=user_id,
                        num_questions=needed,
                    )
                    for pq in pool_questions:
                        eq = ExamQuestion(
                            exam_id=exam.id,
                            text=pq.text,
                            options=pq.options,
                            correct_answer=pq.correct_answer,
                            explanation=pq.explanation,
                            order_index=len(questions) + 1,
                        )
                        self.db.add(eq)
                        self.db.flush()
                        questions.append(eq)

            exam.total_questions = len(questions)
            self.db.commit()

            result = self.exam_result_repo.create(exam_id=exam.id, user_id=user_id)
            result_id = str(result.id)
            is_new = True

        questions = self._shuffle_questions(questions, user_id, exam_id)
        questions = self._shuffle_options(questions, user_id, exam_id)

        return {
            "result_id": result_id,
            "is_new": is_new,
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
                        "options": q.options if isinstance(q.options, list) else json.loads(q.options) if isinstance(q.options, str) else q.options,
                        "order_index": i + 1,
                    }
                    for i, q in enumerate(questions)
                ],
            },
            "time_limit_minutes": int(exam.time_limit_minutes or 60),
        }

    async def _fetch_live_questions(self, exam, user_id: str, needed: int) -> list[dict]:
        """Fetch real-time exam questions using Brave API with cognitive depth focus."""
        subject = exam.subject
        subject_name = subject.name if subject else "General"
        exam_type = exam.exam_type

        topics = (
            self.db.query(Topic)
            .join(Topic.lesson)
            .filter(Lesson.subject_id == exam.subject_id)
            .all()
        )
        topic_names = [t.title for t in topics] if topics else [subject_name]

        selected_topic = random.Random(f"{user_id}:{exam.id}").choice(topic_names)

        questions = await self.ai_service.generate_exam_questions_for_topic(
            subject=subject_name,
            exam_type=exam_type,
            topic=selected_topic,
            num_questions=min(needed, 10),
        )

        return questions

    async def generate_live_questions(self, exam_id: str, user_id: str, num_questions: int) -> list[dict]:
        """Generate fresh questions for an exam in real-time."""
        exam = self.exam_repo.get_with_questions(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        questions = await self._fetch_live_questions(exam, user_id, num_questions)

        rng = random.Random(f"live:{user_id}:{exam_id}:{datetime.now(timezone.utc).isoformat()[:16]}")
        rng.shuffle(questions)

        return [
            {
                "id": f"live_{hash(q['text'][:60])}",
                "text": q["text"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q.get("explanation", ""),
                "difficulty": q.get("difficulty", "hard"),
                "cognitive_level": q.get("cognitive_level", "analysis"),
            }
            for q in questions
        ]

    def start_exam(self, exam_id: str, user_id: str) -> dict:
        """Sync version for existing uses (kept for backward compatibility)."""
        exam = self.exam_repo.get_with_questions(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        in_progress = self.exam_result_repo.get_in_progress(user_id, exam_id)
        if in_progress:
            result_id = str(in_progress.id)
            questions = self._get_existing_questions(exam, result_id)
            is_new = False
        else:
            standards = EXAM_TYPE_STANDARDS.get(exam.exam_type, JAMB_STANDARDS)
            subject_standard = standards.get(exam.subject.slug, {"questions": 50, "minutes": 60})
            target_count = exam.total_questions or subject_standard["questions"] or 50

            existing_qs = list(exam.questions) if exam.questions else []
            questions = list(existing_qs)

            if len(questions) < target_count:
                needed = target_count - len(questions)
                pool_questions = self.pool_service.get_questions_for_exam(
                    subject_id=str(exam.subject_id),
                    user_id=user_id,
                    num_questions=needed,
                )
                for pq in pool_questions:
                    eq = ExamQuestion(
                        exam_id=exam.id,
                        text=pq.text,
                        options=pq.options,
                        correct_answer=pq.correct_answer,
                        explanation=pq.explanation,
                        order_index=len(questions) + 1,
                    )
                    self.db.add(eq)
                    self.db.flush()
                    questions.append(eq)

            exam.total_questions = len(questions)
            self.db.commit()

            result = self.exam_result_repo.create(exam_id=exam.id, user_id=user_id)
            result_id = str(result.id)
            is_new = True

        random.shuffle(questions)

        return {
            "result_id": result_id,
            "is_new": is_new,
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
                        "options": q.options if isinstance(q.options, list) else json.loads(q.options) if isinstance(q.options, str) else q.options,
                        "order_index": i + 1,
                    }
                    for i, q in enumerate(questions)
                ],
            },
            "time_limit_minutes": int(exam.time_limit_minutes or 60),
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
        random.Random(42).shuffle(questions)
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

        try:
            from app.services.analytics_service import AnalyticsService
            analytics = AnalyticsService(self.db)
            analytics.log_event(
                user_id=user_id,
                event_type="exam_completed",
                event_data={
                    "exam_id": str(result.exam_id),
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
                xp_earned = round(20 * (percentage / 100))
                gs.add_xp(user, max(1, xp_earned), reason="exam_completed")
        except Exception:
            pass

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
                    "exam_title": r.exam.title if r.exam else None,
                    "subject_slug": r.exam.subject.slug if r.exam and r.exam.subject else None,
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

    def _get_existing_questions(self, exam, result_id: str):
        existing_answers = self.db.query(ExamAnswer).filter(
            ExamAnswer.result_id == result_id
        ).all()
        answered_q_ids = {a.question_id for a in existing_answers}
        questions = [q for q in exam.questions if q.id not in answered_q_ids]
        if not questions:
            questions = list(exam.questions)
        return questions
