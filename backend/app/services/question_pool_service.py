import random
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.question_pool import QuestionPool, UserSeenQuestion
from app.models.subject import Subject
from app.models.lesson import Topic
from app.services.ai_service import AIService
from typing import Optional

logger = logging.getLogger(__name__)


class QuestionPoolService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    @staticmethod
    def _run_async(coro):
        """Safely run an async coroutine from a sync context."""
        import asyncio
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    def get_questions_for_exam(self, subject_id: str, user_id: str, num_questions: int, topics: list[str] = None) -> list[QuestionPool]:
        seen_ids_q = select(UserSeenQuestion.question_id).where(
            UserSeenQuestion.user_id == user_id
        )
        seen_ids = [row[0] for row in self.db.execute(seen_ids_q).fetchall()]

        query = select(QuestionPool).where(
            QuestionPool.subject_id == subject_id,
            QuestionPool.is_active == True
        )
        if topics:
            query = query.where(QuestionPool.topic.in_(topics))
        if seen_ids:
            query = query.where(QuestionPool.id.notin_(seen_ids))

        all_available = list(self.db.execute(query).scalars().all())
        random.shuffle(all_available)

        if len(all_available) >= num_questions:
            selected = all_available[:num_questions]
        else:
            selected = list(all_available)
            needed = num_questions - len(all_available)
            new_questions = self._generate_questions(subject_id, topics or [], needed)
            selected.extend(new_questions)

        for q in selected:
            q.times_used += 1
            seen = UserSeenQuestion(user_id=user_id, question_id=q.id)
            self.db.add(seen)
        self.db.commit()

        return selected[:num_questions]

    def _generate_questions(self, subject_id: str, topics: list[str], count: int) -> list[QuestionPool]:
        subject = self.db.get(Subject, subject_id)
        if not subject:
            return []

        if not topics:
            topic_objs = (
                self.db.query(Topic)
                .join(Topic.lesson)
                .filter(Topic.lesson.has(subject_id=subject_id))
                .all()
            )
            topics = [t.title for t in topic_objs]

        if not topics:
            return []

        try:
            selected_topic = topics[0] if topics else subject.name
            result_questions = self._run_async(
                self.ai_service.generate_exam_questions_for_topic(
                    subject=subject.name,
                    exam_type="WAEC/JAMB",
                    topic=selected_topic,
                    num_questions=count,
                )
            )
        except Exception as exc:
            logger.error(f"Failed to generate questions via AI: {exc}")
            try:
                result = self.ai_service._generate_questions_from_brave(
                    subject=subject.name,
                    topics=topics,
                    num_questions=count
                )
                result_questions = result.get("questions", [])
            except Exception as exc2:
                logger.error(f"Failed fallback question generation: {exc2}")
                return []

        questions = []
        for q_data in result_questions:
            assigned_topic = q_data.get("topic", "")
            if assigned_topic not in topics:
                assigned_topic = topics[0] if topics else subject.name

            try:
                pool_q = QuestionPool(
                    subject_id=subject_id,
                    topic=assigned_topic,
                    text=q_data["text"],
                    options=q_data.get("options", []),
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data.get("explanation", ""),
                    difficulty=q_data.get("difficulty", "hard"),
                    source="ai_generated",
                )
                self.db.add(pool_q)
                self.db.flush()
                questions.append(pool_q)
            except (KeyError, Exception):
                continue

        self.db.commit()
        return questions[:count]

    def get_questions_for_quiz(self, subject_id: str, user_id: str, num_questions: int, topics: list[str] = None, mark_seen: bool = True) -> list[QuestionPool]:
        seen_ids_q = select(UserSeenQuestion.question_id).where(
            UserSeenQuestion.user_id == user_id
        )
        seen_ids = [row[0] for row in self.db.execute(seen_ids_q).fetchall()]

        query = select(QuestionPool).where(
            QuestionPool.subject_id == subject_id,
            QuestionPool.is_active == True
        )
        if topics:
            query = query.where(QuestionPool.topic.in_(topics))
        if seen_ids:
            query = query.where(QuestionPool.id.notin_(seen_ids))

        all_available = list(self.db.execute(query).scalars().all())
        random.shuffle(all_available)

        if len(all_available) >= num_questions:
            selected = all_available[:num_questions]
        else:
            selected = list(all_available)
            needed = num_questions - len(all_available)
            new_questions = self._generate_questions(subject_id, topics or [], needed)
            selected.extend(new_questions)

        if mark_seen:
            for q in selected:
                q.times_used += 1
                seen = UserSeenQuestion(user_id=user_id, question_id=q.id)
                self.db.add(seen)
            self.db.commit()

        return selected[:num_questions]

    def mark_questions_seen(self, user_id: str, question_ids: list[str]):
        for qid in question_ids:
            existing = self.db.query(UserSeenQuestion).filter(
                UserSeenQuestion.user_id == user_id,
                UserSeenQuestion.question_id == qid,
            ).first()
            if not existing:
                seen = UserSeenQuestion(user_id=user_id, question_id=qid)
                self.db.add(seen)
        self.db.commit()

    def get_available_count(self, subject_id: str, user_id: str) -> int:
        seen_ids_q = select(UserSeenQuestion.question_id).where(
            UserSeenQuestion.user_id == user_id
        )
        seen_ids = [row[0] for row in self.db.execute(seen_ids_q).fetchall()]

        query = select(func.count()).select_from(QuestionPool).where(
            QuestionPool.subject_id == subject_id,
            QuestionPool.is_active == True
        )
        if seen_ids:
            query = query.where(QuestionPool.id.notin_(seen_ids))
        return self.db.execute(query).scalar() or 0
