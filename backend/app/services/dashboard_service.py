from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.repositories.progress import UserProgressRepository
from app.repositories.quiz import QuizAttemptRepository
from app.repositories.exam import ExamResultRepository
from app.repositories.credit import CreditTransactionRepository
from app.repositories.subject import SubjectRepository
from app.core.config import settings


class DashboardService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.progress_repo = UserProgressRepository(db)
        self.quiz_attempt_repo = QuizAttemptRepository(db)
        self.exam_result_repo = ExamResultRepository(db)
        self.credit_repo = CreditTransactionRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.db = db

    def get_dashboard(self, user_id: str) -> dict:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        weekly_used = self.credit_repo.get_weekly_usage(user_id)
        weekly_remaining = max(0, settings.FREE_WEEKLY_CREDITS - weekly_used)

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

        return {
            "welcome_name": user.full_name.split()[0] if user.full_name else "Student",
            "credits": int(user.credits or "0"),
            "weekly_credits_remaining": weekly_remaining,
            "learning_streak": int(user.learning_streak or "0"),
            "recent_activity": [],
            "progress_overview": subject_stats,
            "subject_stats": subject_stats,
            "strong_subjects": strong,
            "weak_subjects": weak,
        }
