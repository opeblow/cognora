from datetime import datetime, date, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.repositories.user import UserRepository
from app.repositories.progress import UserProgressRepository
from app.repositories.quiz import QuizAttemptRepository
from app.repositories.exam import ExamResultRepository
from app.repositories.subject import SubjectRepository
from app.repositories.credit import CreditTransactionRepository
from app.models.quiz import QuizAttempt, QuizAnswer
from app.models.exam import ExamResult
from app.models.analytics import UserAnalytics
from app.models.study_plan import StudyPlanDay


class AnalyticsService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.progress_repo = UserProgressRepository(db)
        self.quiz_attempt_repo = QuizAttemptRepository(db)
        self.exam_result_repo = ExamResultRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.credit_repo = CreditTransactionRepository(db)
        self.db = db

    def get_dashboard(self, user_id: str) -> dict:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        progress = self.progress_repo.get_by_user(user_id)
        subject_stats = []
        for p in progress:
            subject = self.subject_repo.get(p.subject_id)
            if subject:
                subject_stats.append({
                    "subject_id": str(p.subject_id),
                    "subject_name": subject.name,
                    "lessons_completed": int(p.lessons_completed or "0"),
                    "quizzes_taken": int(p.quizzes_taken or "0"),
                    "average_score": float(p.average_score or "0"),
                    "total_study_time_minutes": int(p.total_study_time_minutes or "0"),
                })

        strong = sorted(subject_stats, key=lambda x: x["average_score"], reverse=True)[:3]
        weak = sorted(subject_stats, key=lambda x: x["average_score"])[:3]

        weekly_used = self.credit_repo.get_weekly_usage(user_id)

        return {
            "welcome_name": user.full_name.split()[0] if user.full_name else "Student",
            "credits": int(user.credits or 0),
            "weekly_credits_remaining": max(0, 50 - weekly_used),
            "learning_streak": int(user.learning_streak or 0),
            "recent_activity": self._get_recent_activity(user_id),
            "progress_overview": subject_stats,
            "subject_stats": subject_stats,
            "strong_subjects": strong,
            "weak_subjects": weak,
        }

    def get_analytics(self, user_id: str) -> dict:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        progress = self.progress_repo.get_by_user(user_id)
        quiz_attempts = self.quiz_attempt_repo.get_by_user(user_id)
        exam_results = self.exam_result_repo.get_by_user(user_id)

        subject_ids = list({p.subject_id for p in progress})
        subjects_map = {}
        if subject_ids:
            subjects = self.db.execute(
                select(Subject).where(Subject.id.in_(subject_ids))
            ).scalars().all()
            subjects_map = {str(s.id): s for s in subjects}

        subject_stats = []
        total_quiz = 0
        total_exam = 0
        overall_scores = []

        for p in progress:
            subject = subjects_map.get(str(p.subject_id))
            if subject:
                def safe_int(v):
                    try:
                        return int(v) if v is not None else 0
                    except (ValueError, TypeError):
                        return 0
                def safe_float(v):
                    try:
                        return float(v) if v is not None else 0.0
                    except (ValueError, TypeError):
                        return 0.0
                subject_stats.append({
                    "subject_id": str(p.subject_id),
                    "subject_name": subject.name,
                    "lessons_completed": safe_int(p.lessons_completed),
                    "quizzes_taken": safe_int(p.quizzes_taken),
                    "average_score": safe_float(p.average_score),
                    "total_study_time_minutes": safe_int(p.total_study_time_minutes),
                    "mastery_percentage": self._calculate_mastery(p),
                })

        for a in quiz_attempts:
            if a.percentage:
                try:
                    overall_scores.append(float(a.percentage))
                    total_quiz += 1
                except (ValueError, TypeError):
                    pass

        for e in exam_results:
            if e.percentage:
                try:
                    overall_scores.append(float(e.percentage))
                    total_exam += 1
                except (ValueError, TypeError):
                    pass

        overall_avg = sum(overall_scores) / len(overall_scores) if overall_scores else 0

        strong_subjects = sorted(subject_stats, key=lambda x: x["average_score"], reverse=True)[:3]
        weak_subjects = sorted(subject_stats, key=lambda x: x["average_score"])[:3]

        return {
            "strong_subjects": strong_subjects,
            "weak_subjects": weak_subjects,
            "total_quizzes_taken": total_quiz,
            "total_exams_taken": total_exam,
            "overall_average": round(overall_avg, 2),
            "learning_streak": int(user.learning_streak or 0),
            "total_study_time_minutes": sum(s["total_study_time_minutes"] for s in subject_stats),
            "accuracy_trends": self._get_accuracy_trends(user_id),
            "improvement_rate": self._get_improvement_rate(quiz_attempts),
            "topic_mastery": self._get_topic_mastery(user_id),
        }

    def _get_recent_activity(self, user_id: str, limit: int = 10) -> list[dict]:
        events = (
            self.db.query(UserAnalytics)
            .filter(UserAnalytics.user_id == user_id)
            .order_by(UserAnalytics.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "type": e.event_type,
                "data": e.event_data or {},
                "timestamp": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]

    def _get_accuracy_trends(self, user_id: str) -> list[dict]:
        """Aggregate quiz/exam scores over time for trend visualization."""
        attempts = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.user_id == user_id, QuizAttempt.completed_at.isnot(None))
            .order_by(QuizAttempt.completed_at.asc())
            .all()
        )

        trends = []
        for a in attempts:
            if a.percentage:
                try:
                    trends.append({
                        "date": a.completed_at.isoformat() if a.completed_at else None,
                        "quiz_score": float(a.percentage),
                        "exam_score": None,
                        "study_time_minutes": 0,
                    })
                except (ValueError, TypeError):
                    pass

        results = (
            self.db.query(ExamResult)
            .filter(ExamResult.user_id == user_id, ExamResult.completed_at.isnot(None))
            .order_by(ExamResult.completed_at.asc())
            .all()
        )
        for r in results:
            if r.percentage:
                try:
                    trends.append({
                        "date": r.completed_at.isoformat() if r.completed_at else None,
                        "quiz_score": None,
                        "exam_score": float(r.percentage),
                        "study_time_minutes": 0,
                    })
                except (ValueError, TypeError):
                    pass

        trends.sort(key=lambda t: t["date"] or "")
        return trends[-30:]

    def _get_improvement_rate(self, attempts: list) -> float:
        """Calculate improvement rate as the slope of score over time."""
        if len(attempts) < 2:
            return 0.0

        valid = []
        for a in attempts:
            if a.percentage and a.completed_at:
                try:
                    valid.append((a.completed_at.timestamp(), float(a.percentage)))
                except (ValueError, TypeError):
                    pass

        if len(valid) < 2:
            return 0.0

        valid.sort()
        first_score = valid[0][1]
        last_score = valid[-1][1]
        change = last_score - first_score
        return round(change / max(1, len(valid)), 2)

    def _get_topic_mastery(self, user_id: str) -> list[dict]:
        """Per-subject topic mastery based on quiz performance and study completion."""
        def safe_int(v):
            try:
                return int(v) if v is not None else 0
            except (ValueError, TypeError):
                return 0

        progress = self.progress_repo.get_by_user(user_id)

        subject_ids = list({p.subject_id for p in progress})
        subjects_map = {}
        if subject_ids:
            subjects = self.db.execute(
                select(Subject).where(Subject.id.in_(subject_ids))
            ).scalars().all()
            subjects_map = {str(s.id): s for s in subjects}

        all_attempts = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.user_id == user_id)
            .all()
        )

        attempts_by_subject: dict[str, list] = {}
        for a in all_attempts:
            if a.quiz:
                sid = str(a.quiz.subject_id)
                attempts_by_subject.setdefault(sid, []).append(a)

        mastery = []
        for p in progress:
            subject = subjects_map.get(str(p.subject_id))
            if not subject:
                continue

            subject_attempts = attempts_by_subject.get(str(p.subject_id), [])
            subject_name = subject.name
            quiz_scores = []

            lessons = subject.lessons if hasattr(subject, 'lessons') else []
            total_lessons = max(1, len(lessons))

            for a in subject_attempts:
                if a.percentage:
                    try:
                        quiz_scores.append(float(a.percentage))
                    except (ValueError, TypeError):
                        pass

            avg_quiz = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
            lessons_done = safe_int(p.lessons_completed)
            study_completion = min(100, (lessons_done / total_lessons) * 100)

            mastery_breakdown = {
                "concept_understanding": min(100, avg_quiz * 0.7 + study_completion * 0.3) if avg_quiz > 0 else 0,
                "problem_solving": min(100, avg_quiz * 0.6 + study_completion * 0.4) if avg_quiz > 0 else 0,
                "exam_readiness": min(100, avg_quiz * 0.8 + study_completion * 0.2) if avg_quiz > 0 else 0,
            }

            overall_mastery = sum(mastery_breakdown.values()) / len(mastery_breakdown)

            mastery.append({
                "subject_id": str(p.subject_id),
                "subject_name": subject_name,
                "mastery_percentage": round(overall_mastery, 1),
                "breakdown": {k: round(v, 1) for k, v in mastery_breakdown.items()},
                "quizzes_attempted": len(quiz_scores),
                "lessons_completed": lessons_done,
                "study_completion_percentage": round(study_completion, 1),
            })

        return mastery

    def _calculate_mastery(self, progress) -> float:
        """Quick mastery calculation for per-subject stats."""
        try:
            avg_score = float(progress.average_score) if progress.average_score else 0.0
        except (ValueError, TypeError):
            avg_score = 0.0
        try:
            lessons = int(progress.lessons_completed) if progress.lessons_completed else 0
        except (ValueError, TypeError):
            lessons = 0
        return round(avg_score * 0.7 + min(lessons * 5, 30), 1)

    def log_event(self, user_id: str, event_type: str, event_data: Optional[dict] = None):
        """Log an analytics event (called by other services to stay in sync)."""
        event = UserAnalytics(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data or {},
        )
        self.db.add(event)
        self.db.commit()

    def update_mastery_from_planner(self, user_id: str, subject_id: str):
        """Called by planner when a task is marked done — updates mastery in real-time."""
        progress = self.progress_repo.get_by_user_and_subject(user_id, subject_id)
        if progress:
            attempts = (
                self.db.query(QuizAttempt)
                .filter(QuizAttempt.user_id == user_id)
                .all()
            )
            quiz_scores = []
            for a in attempts:
                if a.quiz and str(a.quiz.subject_id) == subject_id and a.percentage:
                    try:
                        quiz_scores.append(float(a.percentage))
                    except (ValueError, TypeError):
                        pass

            avg = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
            self.log_event(
                user_id,
                "mastery_updated",
                {"subject_id": subject_id, "new_mastery": round(avg, 1)},
            )
