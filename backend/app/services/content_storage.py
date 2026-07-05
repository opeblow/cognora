import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.database.redis import get_redis
from app.models.lesson import Topic
from app.models.textbook_section import TextbookSection
from app.core.errors import AppError

logger = logging.getLogger(__name__)


class ContentStorage:
    def __init__(self, db: Session):
        self.db = db

    async def get_topic_content(self, topic_id: str) -> dict:
        r = await get_redis()
        cache_key = f"content:topic:{topic_id}"
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise AppError("TOPIC_NOT_FOUND", "Topic not found", 404)

        sections = (
            self.db.query(TextbookSection)
            .filter(TextbookSection.topic_id == topic_id)
            .order_by(TextbookSection.section_index)
            .all()
        )

        result = {
            "id": str(topic.id),
            "title": topic.title,
            "html_content": topic.content or "",
            "sections": [
                {
                    "id": str(s.id),
                    "title": s.title,
                    "content": s.content or "",
                    "section_index": s.section_index,
                    "word_count": s.word_count,
                    "is_generated": s.is_generated,
                }
                for s in sections
            ],
        }

        await r.setex(cache_key, 3600, json.dumps(result))
        return result

    async def get_topic_progress(self, user_id: str, topic_id: str) -> dict:
        r = await get_redis()
        key = f"progress:topic:{user_id}:{topic_id}"
        data = await r.get(key)
        if data:
            return json.loads(data)

        return {
            "topic_id": topic_id,
            "completed": False,
            "sections_read": [],
            "total_sections": 0,
            "exercises_attempted": 0,
            "exercises_passed": 0,
            "deep_dives_completed": [],
            "last_position": "0%",
            "time_spent_seconds": 0,
        }

    async def update_topic_progress(self, user_id: str, topic_id: str, update: dict):
        r = await get_redis()
        key = f"progress:topic:{user_id}:{topic_id}"
        current = await self.get_topic_progress(user_id, topic_id)
        current.update(update)

        sections = current.get("sections_read", [])
        total = current.get("total_sections", 0) or len(sections)
        current["completed"] = total > 0 and len(sections) >= total

        await r.setex(key, 86400 * 7, json.dumps(current))

    async def get_deep_dive(self, deep_dive_id: str) -> Optional[dict]:
        r = await get_redis()
        cache_key = f"content:deepdive:{deep_dive_id}"
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)
        return None

    async def cache_deep_dive(self, deep_dive_id: str, content: dict):
        r = await get_redis()
        await r.setex(
            f"content:deepdive:{deep_dive_id}",
            86400 * 7,
            json.dumps(content),
        )

    async def invalidate_topic(self, topic_id: str):
        r = await get_redis()
        await r.delete(f"content:topic:{topic_id}")
        keys = await r.keys(f"progress:topic:*:{topic_id}")
        if keys:
            await r.delete(*keys)
