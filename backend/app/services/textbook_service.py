import json
import hashlib
import logging
from typing import Optional

from app.core.config import settings
from app.database.redis import get_redis

logger = logging.getLogger(__name__)

TEXTBOOK_SECTIONS = [
    {"index": 0, "title": "Learning Objectives & Introduction", "focus": "introduction, learning objectives, real-world relevance, defining the topic from first principles"},
    {"index": 1, "title": "Fundamental Concepts", "focus": "fundamental concepts, definitions, basic notation, and essential background knowledge. Start from absolute basics."},
    {"index": 2, "title": "Core Principles & Theory", "focus": "core principles, laws, theorems, derivations, and the main theoretical framework. Include step-by-step reasoning."},
    {"index": 3, "title": "Worked Examples (Step-by-Step)", "focus": "5+ fully worked examples with detailed step-by-step solutions. Show multiple approaches where applicable."},
    {"index": 4, "title": "Applications & Real-World Context", "focus": "real-world applications, particularly in Nigerian context. Connect theory to practical problems and other topics."},
    {"index": 5, "title": "Advanced Topics & Complex Problems", "focus": "advanced aspects, edge cases, and 3+ challenging problems with complete solutions. Push beyond the basics."},
    {"index": 6, "title": "Common Misconceptions & Exam Tips", "focus": "common student mistakes, tricky exam traps, time-saving techniques, and what WAEC/JAMB examiners look for."},
    {"index": 7, "title": "Practice Exercises (Foundation)", "focus": "10+ practice questions at easy to medium difficulty. Full solutions provided."},
    {"index": 8, "title": "Practice Exercises (Challenge)", "focus": "10+ practice questions at medium to hard difficulty. Full solutions and exam-style marking schemes."},
    {"index": 9, "title": "Summary & Key Formulas", "focus": "comprehensive summary of all key concepts, formulas in plain text, and suggested next topics to study."},
]


def _cache_key(topic_id: str, section_index: int) -> str:
    return f"textbook:{topic_id}:section:{section_index}"


def _plan_cache_key(topic_id: str) -> str:
    return f"textbook:{topic_id}:plan"


class TextbookService:
    def __init__(self):
        self.sections = TEXTBOOK_SECTIONS

    def get_section_plan(self) -> list[dict]:
        return self.sections

    async def get_cached_section(self, topic_id: str, section_index: int) -> Optional[str]:
        try:
            r = await get_redis()
            cached = await r.get(_cache_key(topic_id, section_index))
            if cached:
                return cached
        except Exception as e:
            logger.warning(f"Redis get failed for {topic_id} section {section_index}: {e}")
        return None

    async def cache_section(self, topic_id: str, section_index: int, content: str):
        try:
            r = await get_redis()
            await r.setex(_cache_key(topic_id, section_index), 86400 * 7, content)
        except Exception as e:
            logger.warning(f"Redis set failed for {topic_id} section {section_index}: {e}")

    async def clear_topic_cache(self, topic_id: str):
        try:
            r = await get_redis()
            for sec in self.sections:
                await r.delete(_cache_key(topic_id, sec["index"]))
            await r.delete(_plan_cache_key(topic_id))
        except Exception as e:
            logger.warning(f"Redis clear failed for {topic_id}: {e}")

    async def get_generated_sections(self, topic_id: str) -> list[int]:
        generated = []
        for sec in self.sections:
            content = await self.get_cached_section(topic_id, sec["index"])
            if content:
                generated.append(sec["index"])
        return generated

    def build_section_prompt(
        self,
        subject: str,
        topic: str,
        section_index: int,
        previous_sections: list[str],
    ) -> str:
        if section_index < 0 or section_index >= len(self.sections):
            section_index = 0
        section = self.sections[section_index]
        prev_context = ""
        if previous_sections:
            summaries = []
            for i, content in enumerate(previous_sections):
                if content:
                    words = content.split()[:100]
                    summaries.append(f"[Section {i} summary]: {' '.join(words)}...")
            if summaries:
                prev_context = "\n\nPreviously covered:\n" + "\n".join(summaries)

        prompt = f"""You are writing a section of a textbook chapter on "{topic}" for {subject} (WAEC/NECO/JAMB/GCE/Post-UTME).

CURRENT SECTION ({section_index + 1}/{len(self.sections)}): {section["title"]}
FOCUS: {section["focus"]}

CRITICAL RULES:
1. Use PLAIN TEXT for ALL mathematical expressions and formulas. NEVER use LaTeX.
   - Write "x^2 + y^2 = r^2" NOT "$x^2 + y^2 = r^2$"
   - Write "integral of f(x) dx from a to b" NOT "\\int_a^b f(x) dx"
   - Write "E = mc^2" NOT "$E = mc^2$"
   - Write "square root of (x^2 + y^2)" NOT "\\sqrt{x^2 + y^2}"
   - Write "f'(x) = 2x + 3" NOT "$f'(x) = 2x + 3$"
   - Write "a/b" for fractions, "a^b" for exponents, "a_n" for subscripts
   - Write "x -> infinity" for limits, "delta x" for difference
   - Write "sum of i=1 to n of a_i" for summation notation

2. Output clean semantic HTML. Use these tags:
   - <h3> for section title
   - <h4> for subsection titles
   - <p> for paragraphs
   - <strong> for key terms and formulas
   - <ul>/<ol> + <li> for lists
   - <pre> for formulas, equations, and solution steps (each on its own line)
   - <table> for comparisons, with <thead>/<tbody>/<tr>/<th>/<td>

3. Every worked example MUST follow this structure:
   <h4>Example X: [Title]</h4>
   <p><strong>Problem:</strong> [question text]</p>
   <p><strong>Solution (Step-by-Step):</strong></p>
   <pre>
   Step 1: ...
   Step 2: ...
   ...
   </pre>
   <p><strong>Answer:</strong> [final answer]</p>

4. Write in clear, formal academic English suitable for senior secondary students.
5. Each section should be detailed but self-contained (500-1500 words).
6. Connect to exam syllabuses (WAEC, NECO, JAMB, Post-UTME) where relevant.

Write only the HTML content for this section. Do NOT include any meta-commentary. Start directly with the <h3> tag."""
        prompt += prev_context
        return prompt


async def generate_section_content(
    subject: str,
    topic: str,
    section_index: int,
    previous_sections: list[str],
) -> str:
    from app.services.ai_service import AIService

    service = TextbookService()
    prompt = service.build_section_prompt(subject, topic, section_index, previous_sections)

    ai = AIService()
    try:
        content = await ai.generate_section(prompt, section_index)
        return content
    except Exception as e:
        logger.error(f"Failed to generate section {section_index}: {e}")
        raise
