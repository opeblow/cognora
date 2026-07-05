import random
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.study_plan import StudyPlanRepository
from app.repositories.subject import SubjectRepository
from app.repositories.quiz import QuizAttemptRepository
from app.repositories.exam import ExamResultRepository
from app.repositories.lesson import LessonRepository
from app.models.study_plan import StudyPlan, StudyPlanDay
from app.models.quiz import QuizAttempt, QuizAnswer
from app.services.ai_service import AIService


class StudyPlanService:
    def __init__(self, db: Session):
        self.repo = StudyPlanRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.quiz_attempt_repo = QuizAttemptRepository(db)
        self.exam_result_repo = ExamResultRepository(db)
        self.lesson_repo = LessonRepository(db)
        self.ai_service = AIService()
        self.db = db

    def get_plans(self, user_id: str) -> dict:
        plans = self.repo.get_by_user(user_id)
        return {
            "plans": [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "description": p.description,
                    "plan_type": p.plan_type,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "end_date": p.end_date.isoformat() if p.end_date else None,
                    "is_active": p.is_active,
                    "days": [
                        {
                            "id": str(d.id),
                            "date": d.date.isoformat() if d.date else None,
                            "subjects": d.subjects or [],
                            "topics": d.topics or [],
                            "duration_minutes": d.duration_minutes,
                            "is_completed": d.is_completed,
                            "notes": d.notes,
                        }
                        for d in p.days
                    ],
                }
                for p in plans
            ],
            "total": len(plans),
        }

    def get_plan(self, plan_id: str, user_id: str) -> dict:
        plan = self.repo.get_with_days(plan_id)
        if not plan or str(plan.user_id) != user_id:
            raise ValueError("Study plan not found")
        return {
            "id": str(plan.id),
            "title": plan.title,
            "description": plan.description,
            "plan_type": plan.plan_type,
            "start_date": plan.start_date.isoformat() if plan.start_date else None,
            "end_date": plan.end_date.isoformat() if plan.end_date else None,
            "is_active": plan.is_active,
            "days": [
                {
                    "id": str(d.id),
                    "date": d.date.isoformat() if d.date else None,
                    "subjects": d.subjects or [],
                    "topics": d.topics or [],
                    "duration_minutes": d.duration_minutes,
                    "is_completed": d.is_completed,
                    "notes": d.notes,
                }
                for d in plan.days
            ],
        }

    def _scheduling_algorithm(
        self,
        subjects: list[str],
        start_date: date,
        end_date: date,
        topics_per_subject: dict[str, list[str]] = None,
    ) -> list[dict]:
        """Break subjects into daily micro-tasks using a round-robin + spaced repetition approach.

        Algorithm:
        1. Calculate total available days.
        2. Partition subjects evenly across days.
        3. Within each subject, distribute topics with increasing difficulty.
        4. Insert review sessions at spaced intervals (1, 3, 7 days after first study).
        """
        total_days = (end_date - start_date).days + 1
        if total_days <= 0:
            total_days = 1

        tasks = []
        day_offset = 0

        subject_cycle = subjects.copy()
        random.Random(str(start_date)).shuffle(subject_cycle)

        days_per_subject = max(1, total_days // len(subjects))
        review_intervals = [1, 3, 7]

        for subj_idx, subject_name in enumerate(subject_cycle):
            subj_topics = topics_per_subject.get(subject_name, []) if topics_per_subject else []
            if not subj_topics:
                subj_topics = [f"{subject_name} - Core Concepts"]

            tasks_per_day = max(1, len(subj_topics) // days_per_subject)
            topic_idx = 0

            for day_in_subject in range(days_per_subject):
                current_date = start_date + timedelta(days=day_offset)
                if current_date > end_date:
                    break

                daily_topics = subj_topics[topic_idx : topic_idx + tasks_per_day]
                if not daily_topics:
                    daily_topics = [f"{subject_name} - Revision"]
                topic_idx += tasks_per_day
                if topic_idx >= len(subj_topics):
                    topic_idx = 0

                session_minutes = min(120, 30 + day_in_subject * 5)

                tasks.append({
                    "date": current_date,
                    "subjects": [subject_name],
                    "topics": daily_topics,
                    "duration_minutes": str(session_minutes),
                })

                for interval in review_intervals:
                    review_date = current_date + timedelta(days=interval)
                    if review_date <= end_date:
                        tasks.append({
                            "date": review_date,
                            "subjects": [subject_name],
                            "topics": [f"Review: {t}" for t in daily_topics],
                            "duration_minutes": str(max(20, session_minutes // 2)),
                        })

                day_offset += 1

        tasks.sort(key=lambda t: t["date"])

        seen_dates = {}
        deduped = []
        for task in tasks:
            key = (task["date"], task["subjects"][0], task["topics"][0])
            if key not in seen_dates:
                deduped.append(task)
                seen_dates[key] = True

        return deduped

    def create_plan(
        self,
        user_id: str,
        title: str,
        description: Optional[str],
        plan_type: str,
        start_date: date,
        end_date: Optional[date],
        subjects: list[str],
        use_ai: bool = False,
    ) -> dict:
        if not end_date:
            end_date = start_date + timedelta(days=30)

        subject_objs = {s.name: s for s in self.subject_repo.get_all()[0]}
        valid_subjects = [s for s in subjects if s in subject_objs or True]

        topics_per_subject = {}
        for s_name in valid_subjects:
            lessons = self.lesson_repo.get_by_subject(subject_objs[s_name].id) if s_name in subject_objs else []
            topics = []
            for lesson in lessons:
                lesson_topics = self.lesson_repo.get_topics(lesson.id)
                topics.extend(t.title for t in lesson_topics[:5])
            topics_per_subject[s_name] = topics if topics else [f"{s_name} - Core Topics"]

        plan = self.repo.create(
            user_id=user_id,
            title=title,
            description=description,
            plan_type=plan_type,
            start_date=start_date,
            end_date=end_date,
            is_active="true",
        )

        daily_tasks = self._scheduling_algorithm(
            subjects=valid_subjects,
            start_date=start_date,
            end_date=end_date,
            topics_per_subject=topics_per_subject,
        )

        for task in daily_tasks:
            self.repo.add_day(
                plan_id=plan.id,
                date=task["date"],
                subjects=task["subjects"],
                topics=task["topics"],
                duration_minutes=task["duration_minutes"],
                is_completed="false",
            )

        return self.get_plan(plan.id, user_id)

    def mark_day_completed(self, day_id: str, user_id: str) -> dict:
        day = self.repo.get_day(day_id)
        if not day:
            raise ValueError("Day not found")

        plan = self.repo.get(day.study_plan_id)
        if not plan or str(plan.user_id) != user_id:
            raise ValueError("Day not found in your plans")

        day.is_completed = "true"
        day.notes = f"Completed at {datetime.now(timezone.utc).isoformat()}"
        self.db.commit()

        return {
            "id": str(day.id),
            "date": day.date.isoformat() if day.date else None,
            "is_completed": day.is_completed,
        }

    def check_and_suggest_reviews(self, user_id: str, quiz_attempt_id: str) -> Optional[dict]:
        """Called after quiz submission. If score is low, inserts a review task."""
        attempt = self.quiz_attempt_repo.get(quiz_attempt_id)
        if not attempt:
            return None

        score = int(attempt.score or "0")
        total = int(attempt.total or "1")
        percentage = (score / total * 100) if total > 0 else 0

        if percentage >= 60:
            return None

        quiz = attempt.quiz
        subject_id = str(quiz.subject_id) if quiz else None
        subject = self.subject_repo.get(subject_id) if subject_id else None
        subject_name = subject.name if subject else "General"

        review_topic = f"Review: Weak areas in {quiz.title if quiz else 'quiz'}"
        answers = self.db.query(QuizAnswer).filter(
            QuizAnswer.attempt_id == attempt.id,
            QuizAnswer.is_correct == False
        ).all()

        weak_topics = []
        for ans in answers[:3]:
            q = ans.question if hasattr(ans, 'question') else None
            if q and hasattr(q, 'text'):
                weak_topics.append(q.text[:80])

        review_title = f"Auto-Review: {quiz.title if quiz else 'Strengthen Weak Areas'}"
        today = date.today()

        plan = self.repo.create(
            user_id=user_id,
            title=review_title,
            description=f"Review session generated due to score of {percentage:.0f}% on {quiz.title if quiz else 'quiz'}",
            plan_type="review",
            start_date=today,
            end_date=today + timedelta(days=3),
            is_active="true",
        )

        topics_to_review = weak_topics if weak_topics else [review_topic]
        for i, topic in enumerate(topics_to_review):
            task_date = today + timedelta(days=i)
            self.repo.add_day(
                plan_id=plan.id,
                date=task_date,
                subjects=[subject_name],
                topics=[topic],
                duration_minutes="30",
                is_completed="false",
            )

        return {
            "plan_id": str(plan.id),
            "title": review_title,
            "reason": f"Score was {percentage:.0f}% — review session created",
            "days": len(topics_to_review),
        }

    def get_today_tasks(self, user_id: str) -> dict:
        today = date.today()
        days = self.repo.get_days_in_range(user_id, today, today)
        return {
            "date": today.isoformat(),
            "tasks": [
                {
                    "id": str(d.id),
                    "plan_id": str(d.study_plan_id),
                    "subjects": d.subjects or [],
                    "topics": d.topics or [],
                    "duration_minutes": d.duration_minutes,
                    "is_completed": d.is_completed,
                }
                for d in days
            ],
            "total": len(days),
        }

    def get_weekly_calendar(self, user_id: str, week_start: Optional[str] = None) -> dict:
        if week_start:
            start = date.fromisoformat(week_start)
        else:
            today = date.today()
            start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

        days = self.repo.get_days_in_range(user_id, start, end)
        calendar = {}
        for d in days:
            d_str = d.date.isoformat() if d.date else None
            if d_str not in calendar:
                calendar[d_str] = []
            calendar[d_str].append({
                "id": str(d.id),
                "plan_id": str(d.study_plan_id),
                "subjects": d.subjects or [],
                "topics": d.topics or [],
                "duration_minutes": d.duration_minutes,
                "is_completed": d.is_completed,
            })

        return {"start_date": start.isoformat(), "end_date": end.isoformat(), "calendar": calendar}
