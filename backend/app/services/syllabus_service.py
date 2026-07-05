import json
import logging
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.redis import get_redis

logger = logging.getLogger(__name__)


SYLLABUS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "syllabi"


class SyllabusService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    async def get_syllabus(self, exam_board: str, subject: str) -> dict:
        cache_key = f"syllabus:{exam_board}:{subject}"
        r = await get_redis()
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

        syllabus = self._load_from_disk(exam_board, subject)
        if syllabus:
            await r.setex(cache_key, 86400, json.dumps(syllabus))
        return syllabus or self._default_syllabus(subject)

    def _load_from_disk(self, exam_board: str, subject: str) -> Optional[dict]:
        file_path = SYLLABUS_DIR / exam_board.lower() / f"{subject.lower().replace(' ', '_')}.json"
        if not file_path.exists():
            logger.warning(f"Syllabus file not found: {file_path}")
            return None
        with open(file_path) as f:
            return json.load(f)

    def _default_syllabus(self, subject: str) -> dict:
        return {
            "exam_board": "WAEC",
            "subject": subject,
            "year": "2026",
            "modules": [],
        }

    async def build_syllabus_context(self, exam_board: str, subject: str, topic_title: str) -> str:
        syllabus = await self.get_syllabus(exam_board, subject)
        for module in syllabus.get("modules", []):
            for topic in module.get("topics", []):
                if topic.get("title", "").lower() == topic_title.lower():
                    return f"""
EXAM BOARD: {exam_board.upper()}
SUBJECT WEIGHT: This topic exam weight = {module.get('weight_in_exam', 'N/A')}%
EXAMINATION FOCUS: {', '.join(topic.get('examination_focus', []))}
TYPICAL QUESTION STYLE: {topic.get('typical_question_style', 'Standard')}
PAST QUESTIONS APPEARED IN: {', '.join(topic.get('past_question_years', []))}
DIFFICULTY: {topic.get('difficulty_rating', 'medium')}
"""
        return "No syllabus data available. Generate standard curriculum-aligned content."

    async def verify_alignment(self, html_content: str, exam_board: str, subject: str, topic_title: str) -> dict:
        syllabus = await self.get_syllabus(exam_board, subject)
        text_lower = html_content.lower()

        for module in syllabus.get("modules", []):
            for topic in module.get("topics", []):
                if topic.get("title", "").lower() == topic_title.lower():
                    uncovered = []
                    focus_points = topic.get("examination_focus", [])
                    for point in focus_points:
                        keywords = point.lower().split()
                        match_count = sum(1 for kw in keywords if kw in text_lower)
                        coverage = match_count / max(len(keywords), 1)
                        if coverage < 0.3:
                            uncovered.append({
                                "focus_point": point,
                                "coverage": round(coverage, 2),
                            })
                    return {
                        "aligned": len(uncovered) == 0,
                        "coverage": round(1 - len(uncovered) / max(len(focus_points), 1), 2),
                        "uncovered_areas": uncovered,
                    }

        return {"aligned": True, "coverage": 1.0, "uncovered_areas": []}
