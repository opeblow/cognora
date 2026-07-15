import json
import logging
from typing import Optional
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.syllabus_service import SyllabusService
from app.services.content_storage import ContentStorage
from app.services.ai_service import AIService
from app.database.redis import get_redis
from app.core.errors import AppError

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_STAGE3 = """You are Cognora's Senior Curriculum Designer. You write
university-preparatory textbook content for West African secondary
students (WAEC/JAMB/NECO). Your writing must be:
- Precise but conversational (reading age: 16-18)
- Rich with real-world Nigerian/African examples
- Optimised for mobile screens (short paragraphs, bullet summaries)
- Self-contained (no assumed knowledge beyond prerequisites)

CRITICAL: All mathematical expressions MUST use plain text notation ONLY.
Never use LaTeX. Use x^2 for exponents, a/b for fractions, sqrt(x) for roots.
Write formulas like: x = (-b +/- sqrt(b^2 - 4ac)) / 2a

Use HTML tags: h3/h4 for headings, p for text, strong for key terms,
ul/ol for lists, pre for formulas/solutions, table for comparisons.

Every worked example MUST have: Problem, Step-by-step solution, Final answer.
"""


class CurriculumPipeline:
    def __init__(self):
        self.async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)
        self.syllabus_service = SyllabusService()
        self.ai_service = AIService()

    async def generate_full_subject(self, subject: str, exam_board: str = "WAEC") -> str:
        syllabus = await self.syllabus_service.get_syllabus(exam_board, subject)
        subject_id = f"{subject.lower().replace(' ', '_')}_{exam_board.lower()}"
        r = await get_redis()

        for module in syllabus.get("modules", []):
            for topic_data in module.get("topics", []):
                exists = await r.get(f"content:topic:{subject_id}:{topic_data['id']}")
                if exists:
                    logger.info(f"Skipping existing topic: {topic_data['title']}")
                    continue

                content = await self._generate_topic(subject, exam_board, module, topic_data)
                await r.setex(
                    f"content:topic:{subject_id}:{topic_data['id']}",
                    86400 * 7,
                    json.dumps(content),
                )
                logger.info(f"Generated topic: {topic_data['title']}")

        return subject_id

    async def _generate_topic(self, subject: str, exam_board: str, module: dict, topic_data: dict) -> dict:
        context = await self.syllabus_service.build_syllabus_context(exam_board, subject, topic_data["title"])

        content = await self._stage3_topic(subject, topic_data["title"], context)

        alignment = await self.syllabus_service.verify_alignment(
            content.get("html_content", ""), exam_board, subject, topic_data["title"]
        )

        if not alignment["aligned"] and alignment["coverage"] < 0.8:
            gap_prompt = f"Re-generate covering these missing areas: {alignment['uncovered_areas']}"
            content = await self._stage3_topic(subject, topic_data["title"], context + gap_prompt)

        return {
            "topic_id": topic_data["id"],
            "title": topic_data["title"],
            "content": content,
            "alignment": alignment,
            "module_id": module.get("id"),
            "exam_board": exam_board,
        }

    async def _stage3_topic(self, subject: str, topic_title: str, context: str) -> dict:
        cache_key = f"curriculum:stage3:{subject}:{topic_title.lower().replace(' ', '_')}"
        r = await get_redis()
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

        prompt = f"""SUBJECT: {subject}
TOPIC: {topic_title}
{context}

Write the complete textbook section for this topic. Include:
1. A hook paragraph connecting to everyday experience
2. Core theory with every new term defined inline
3. 5+ worked examples — each with Problem, Step-by-step solution, Final answer
4. A "Watch Out!" callout for each common mistake
5. A real-world application sidebar (Nigerian context preferred)

Return valid JSON:
{{
  "html_content": "full HTML with class annotations",
  "word_count": 1800,
  "key_terms": [{{"term": "...", "definition": "..."}}],
  "worked_examples": [{{"id": 1, "problem": "...", "solution_steps": ["..."], "final_answer": "...", "annotation": "..."}}],
  "common_mistakes": [{{"mistake": "...", "correction": "..."}}],
  "real_world_application": "...",
  "estimated_read_time_minutes": 12
}}"""

        response = await self.async_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_STAGE3},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=4096,
        )

        raw = response.choices[0].message.content
        if not raw:
            raise ValueError("OpenAI returned empty content for stage3 topic generation")
        result = json.loads(raw)
        await r.setex(cache_key, 86400, json.dumps(result))
        return result

    async def generate_grounded_question(self, subject: str, topic_title: str, difficulty: str = "medium", _depth: int = 0) -> dict:
        from app.services.grounding_service import GroundingService

        if _depth >= 3:
            return {"questions": [], "note": "Failed to generate non-contradicted question after 3 attempts"}

        draft = self.ai_service.generate_quiz(subject, topic_title, difficulty, num_questions=1)

        grounding = GroundingService()
        for q in draft.get("questions", []):
            verdicts = await grounding.verify_question(q["text"], q.get("correct_answer", ""))
            q["grounding"] = verdicts

            rejected = [v for v in verdicts if v["status"] == "contradicted"]
            if rejected:
                return await self.generate_grounded_question(subject, topic_title, difficulty, _depth + 1)

        return draft

    async def stage5_weave(self, subject: str, exam_board: str, module_id: str, topic_ids: list[str]) -> dict:
        r = await get_redis()
        context_parts = []
        for tid in topic_ids:
            cached = await r.get(f"content:topic:{subject}:{tid}")
            if cached:
                data = json.loads(cached)
                context_parts.append(f"Topic: {data['title']}\nSummary: {data['content'].get('html_content', '')[:500]}")

        contexts = "\n\n".join(context_parts[:5])

        prompt = f"""Given these topics in the same module, create a cumulative review:
{contexts}

Return JSON:
{{
  "module_roadmap": "How these topics connect",
  "cumulative_questions": [{{"question": "...", "answer": "...", "topics_involved": ["topic_ids"]}}],
  "mock_exam": {{"time_allowed_minutes": 30, "total_marks": 20, "questions": [...]}}
}}"""

        response = await self.async_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You create cumulative module reviews for WAEC/NECO/JAMB students."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=3000,
        )

        raw = response.choices[0].message.content
        if not raw:
            raise ValueError("OpenAI returned empty content for stage5 weave")
        return json.loads(raw)
