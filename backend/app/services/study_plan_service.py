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

FOCUS_TIPS = [
    "Put your phone on silent and keep it face-down. Distractions kill focus.",
    "Study in short bursts. 45 min focus beats 2 hours of distraction.",
    "No social media during this session. You can check it after.",
    "Close every tab you don't need. Your future self will thank you.",
    "Drink water before you start. Dehydration kills concentration.",
    "Tell someone you're studying so they don't interrupt you.",
    "Start with the hardest topic while your brain is fresh.",
    "Write key points by hand. It helps you remember better.",
    "If your mind wanders, write the thought down and come back to it.",
    "Reward yourself after this session — but not with social media.",
]


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

    def delete_plan(self, plan_id: str, user_id: str) -> bool:
        plan = self.repo.get_with_days(plan_id)
        if not plan or str(plan.user_id) != user_id:
            return False
        self.db.delete(plan)
        self.db.commit()
        return True

    def _get_subject_scores(self, user_id: str, subjects: list[str]) -> dict[str, float]:
        """Get average quiz scores per subject for adaptive weighting."""
        from app.models.subject import Subject
        scores: dict[str, float] = {}
        for s_name in subjects:
            subj = self.db.query(Subject).filter(Subject.name == s_name).first()
            if not subj:
                scores[s_name] = 50.0
                continue
            attempts = (
                self.db.query(QuizAttempt)
                .join(QuizAttempt.quiz)
                .filter(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.quiz.has(subject_id=subj.id),
                )
                .order_by(QuizAttempt.created_at.desc())
                .limit(10)
                .all()
            )
            if attempts:
                total = 0
                for a in attempts:
                    s = int(a.score or "0")
                    t = int(a.total or "1")
                    total += (s / t * 100) if t > 0 else 0
                scores[s_name] = total / len(attempts)
            else:
                scores[s_name] = 50.0
        return scores

    def _scheduling_algorithm(
        self,
        subjects: list[str],
        start_date: date,
        end_date: date,
        hours_per_day: float,
        subject_topics: dict[str, list[str]] = None,
        subject_weights: dict[str, float] = None,
    ) -> list[dict]:
        """Create a realistic daily study timetable with breaks.

        Algorithm:
        1. Build a master topic queue: each topic is a "study block" (~45 min).
        2. Each day: fill available hours with study blocks + 10-min breaks.
        3. Spread subjects across the week (no two hard subjects back-to-back).
        4. Add a focus tip to every day.
        5. If topics run out before the plan ends, cycle back for revision.
        """
        total_days = (end_date - start_date).days + 1
        if total_days <= 0:
            total_days = 1

        total_available_minutes = int(hours_per_day * 60)
        block_minutes = 45
        break_minutes = 10

        weights = subject_weights or {s: 1.0 for s in subjects}
        max_w = max(weights.values()) if weights else 1.0
        normalized = {s: max(0.5, weights[s] / max_w) for s in weights}

        topic_queue = []
        for subj in subjects:
            topics = (subject_topics or {}).get(subj, [])
            if not topics:
                topics = [f"{subj} — Core Concepts"]
            repeat = max(1, int(normalized.get(subj, 1.0) * 3))
            for _ in range(repeat):
                for t in topics:
                    topic_queue.append({"subject": subj, "topic": t, "is_revision": False})

        if not topic_queue:
            topic_queue = [{"subject": subjects[0], "topic": f"{subjects[0]} — Core Concepts", "is_revision": False}]

        all_tasks = []
        topic_idx = 0
        tip_idx = 0
        day_count = 0

        while day_count < total_days:
            current_date = start_date + timedelta(days=day_count)
            day_minutes_used = 0
            day_blocks = []
            day_subjects_used = set()

            while day_minutes_used + block_minutes <= total_available_minutes:
                if topic_idx >= len(topic_queue):
                    topic_idx = 0

                item = topic_queue[topic_idx]
                topic_idx += 1

                label = f"Revision: {item['topic']}" if item["is_revision"] else item["topic"]
                remaining = total_available_minutes - day_minutes_used - break_minutes
                actual_block = min(block_minutes, remaining)

                if actual_block < 15:
                    break

                day_blocks.append({
                    "subject": item["subject"],
                    "topic": label,
                    "duration": actual_block,
                })
                day_subjects_used.add(item["subject"])
                day_minutes_used += actual_block + break_minutes

            if not day_blocks:
                topic_queue[topic_idx % len(topic_queue)]["is_revision"] = True
                day_count += 1
                continue

            total_session = sum(b["duration"] for b in day_blocks)
            subjects_list = list(day_subjects_used)
            topics_list = [b["topic"] for b in day_blocks]
            tip = FOCUS_TIPS[tip_idx % len(FOCUS_TIPS)]
            tip_idx += 1

            session_parts = []
            for i, b in enumerate(day_blocks):
                session_parts.append(f"{b['topic']} ({b['duration']} min)")
                if i < len(day_blocks) - 1:
                    session_parts.append(f"--- {break_minutes}-min break ---")

            all_tasks.append({
                "date": current_date,
                "subjects": subjects_list,
                "topics": session_parts,
                "duration_minutes": str(total_session),
                "notes": f"Focus tip: {tip}",
            })

            day_count += 1

        for item in topic_queue:
            item["is_revision"] = True

        remaining_days = total_days - len(all_tasks)
        if remaining_days > 0 and topic_queue:
            topic_idx = 0
            for i in range(remaining_days):
                current_date = start_date + timedelta(days=len(all_tasks))
                day_minutes_used = 0
                day_blocks = []

                while day_minutes_used + block_minutes <= total_available_minutes:
                    if topic_idx >= len(topic_queue):
                        topic_idx = 0
                    item = topic_queue[topic_idx]
                    topic_idx += 1
                    remaining = total_available_minutes - day_minutes_used - break_minutes
                    actual_block = min(block_minutes, remaining)
                    if actual_block < 15:
                        break
                    day_blocks.append({
                        "subject": item["subject"],
                        "topic": f"Revision: {item['topic']}",
                        "duration": actual_block,
                    })
                    day_minutes_used += actual_block + break_minutes

                if day_blocks:
                    total_session = sum(b["duration"] for b in day_blocks)
                    subjects_list = list(set(b["subject"] for b in day_blocks))
                    topics_list = [b["topic"] for b in day_blocks]
                    tip = FOCUS_TIPS[tip_idx % len(FOCUS_TIPS)]
                    tip_idx += 1

                    session_parts = []
                    for j, b in enumerate(day_blocks):
                        session_parts.append(f"{b['topic']} ({b['duration']} min)")
                        if j < len(day_blocks) - 1:
                            session_parts.append(f"--- {break_minutes}-min break ---")

                    all_tasks.append({
                        "date": current_date,
                        "subjects": subjects_list,
                        "topics": session_parts,
                        "duration_minutes": str(total_session),
                        "notes": f"Focus tip: {tip}",
                    })

        all_tasks.sort(key=lambda t: t["date"])
        return all_tasks

    def create_plan(
        self,
        user_id: str,
        title: str,
        description: Optional[str],
        plan_type: str,
        start_date: date,
        end_date: Optional[date],
        subjects: list[str],
        hours_per_day: float = 2.0,
        subject_topics: Optional[dict[str, list[str]]] = None,
        use_ai: bool = False,
    ) -> dict:
        if not end_date:
            end_date = start_date + timedelta(days=30)

        hours_per_day = max(0.5, min(12.0, hours_per_day))

        if not subject_topics:
            subject_topics = {}
            subject_objs = {s.name: s for s in self.subject_repo.get_all()[0]}
            for s_name in subjects:
                if s_name in subject_objs:
                    lessons = self.lesson_repo.get_by_subject(subject_objs[s_name].id)
                    topics = []
                    for lesson in lessons:
                        lesson_topics = self.lesson_repo.get_topics(lesson.id)
                        topics.extend(t.title for t in lesson_topics[:5])
                    subject_topics[s_name] = topics if topics else [f"{s_name} — Core Topics"]
                else:
                    subject_topics[s_name] = [f"{s_name} — Core Topics"]

        plan = self.repo.create(
            user_id=user_id,
            title=title,
            description=description,
            plan_type=plan_type,
            start_date=start_date,
            end_date=end_date,
            is_active="true",
        )

        subject_scores = self._get_subject_scores(user_id, subjects)
        subject_weights = {}
        for s_name, score in subject_scores.items():
            subject_weights[s_name] = max(0.5, (100 - score) / 100 * 2)

        daily_tasks = self._scheduling_algorithm(
            subjects=subjects,
            start_date=start_date,
            end_date=end_date,
            hours_per_day=hours_per_day,
            subject_topics=subject_topics,
            subject_weights=subject_weights,
        )

        for task in daily_tasks:
            self.repo.add_day(
                plan_id=plan.id,
                date=task["date"],
                subjects=task["subjects"],
                topics=task["topics"],
                duration_minutes=task["duration_minutes"],
                is_completed="false",
                notes=task.get("notes"),
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
        result = []
        for d in days:
            result.append({
                "id": str(d.id),
                "plan_id": str(d.study_plan_id),
                "date": d.date.isoformat() if d.date else None,
                "subjects": d.subjects or [],
                "topics": d.topics or [],
                "duration_minutes": d.duration_minutes,
                "is_completed": d.is_completed,
            })

        return {"start_date": start.isoformat(), "end_date": end.isoformat(), "days": result}
