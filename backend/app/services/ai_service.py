import asyncio
from app.core.config import settings
from typing import Optional
import json
import logging
import re
import httpx
import openai
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)

_openai_client: Optional[OpenAI] = None
_async_openai_client: Optional[AsyncOpenAI] = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)
    return _openai_client


def _get_async_openai_client() -> AsyncOpenAI:
    global _async_openai_client
    if _async_openai_client is None:
        _async_openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)
    return _async_openai_client


class AIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.brave_api_key = settings.BRAVE_API_KEY

    @property
    def client(self) -> OpenAI:
        return _get_openai_client()

    @property
    def async_client(self) -> AsyncOpenAI:
        return _get_async_openai_client()

    def _call_openai(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise ValueError("AI service authentication failed. Please check the API key.")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}")
            raise ValueError("AI service is currently busy. Please try again in a moment.")
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI timeout error: {e}")
            raise ValueError("AI service timed out. Please try again.")
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}")
            raise ValueError("Could not connect to AI service. Please check your internet connection.")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError("AI service encountered an error. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}")
            raise ValueError("An unexpected error occurred. Please try again.")

    def tutor_chat(self, message: str, subject: Optional[str] = None, context: Optional[list[dict]] = None) -> dict:
        system_prompt = """You are Cognora AI, an expert tutor for Nigerian secondary school students preparing for WAEC, NECO, GCE, JAMB, and Post-UTME examinations.

Rules:
1. Adapt explanations to the student's level (ask if unsure)
2. Give clear, practical examples from the Nigerian curriculum
3. Generate practice questions after explanations
4. Break down complex topics into simple steps
5. Use proper educational terminology
6. Reference specific exam syllabuses when relevant
7. Encourage active learning with exercises
8. Give textbook-quality detailed explanations — treat each topic as if writing a full textbook chapter

Keep responses structured and engaging. Use markdown for formatting."""

        if subject:
            system_prompt += f"\nCurrent subject: {subject}"

        messages_list = [{"role": "system", "content": system_prompt}]
        if context:
            messages_list.extend(context[-10:])
        messages_list.append({"role": "user", "content": message})

        response = self._call_openai(messages_list)
        return {"response": response, "suggestions": []}

    def _brave_search(self, query: str, count: int = 10) -> list[dict]:
        if not self.brave_api_key:
            logger.warning("No Brave API key configured")
            return []
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": count},
                    headers={"X-Subscription-Token": self.brave_api_key},
                )
                resp.raise_for_status()
                data = resp.json()
                results = []
                for item in data.get("web", {}).get("results", []):
                    desc = item.get("description", "") or ""
                    title = item.get("title", "") or ""
                    results.append({"title": title, "snippet": desc, "url": item.get("url", "")})
                    if item.get("extra_snippets"):
                        for s in item["extra_snippets"]:
                            results.append({"title": title, "snippet": s, "url": item.get("url", "")})
                return results
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []

    def _parse_exam_questions(self, results: list[dict], subject: str, topic: str, max_q: int) -> list[dict]:
        questions = []
        seen_texts = set()

        for r in results:
            text = f"{r['title']} {r['snippet']}"
            blocks = re.split(r'(?:(?:\d+)[.\)])\s*', text)
            for block in blocks:
                block = block.strip()
                if not block or len(block) < 40:
                    continue

                opt_pattern = r'(?:^|\s)([A-D])[\)\.]\s*[A-Z]'
                options = re.findall(opt_pattern, block)
                if len(options) < 2:
                    continue

                opt_lines = re.split(r'\s*([A-D])[\)\.]\s*', block)
                option_dict = {}
                question_text = ""
                for i, part in enumerate(opt_lines):
                    part = part.strip()
                    if part in ("A", "B", "C", "D") and i + 1 < len(opt_lines):
                        option_dict[part] = opt_lines[i + 1].strip().rstrip(".,;")
                    elif not question_text and len(part) > 15:
                        question_text = part

                if len(option_dict) >= 2 and question_text:
                    q_key = question_text[:60].lower()
                    if q_key in seen_texts:
                        continue
                    seen_texts.add(q_key)

                    formatted = []
                    for letter in ("A", "B", "C", "D"):
                        if letter in option_dict:
                            formatted.append(f"{letter}) {option_dict[letter]}")

                    explanation = r.get("url", "")
                    if explanation:
                        explanation = f"Source: {explanation}"

                    questions.append({
                        "text": question_text,
                        "options": formatted,
                        "correct_answer": "",
                        "explanation": explanation,
                        "difficulty": "hard",
                        "topic": topic,
                    })

                if len(questions) >= max_q:
                    return questions

        return questions

    def generate_quiz_questions(self, subject: str, topic: str, num_questions: int = 5, difficulty: str = "hard") -> dict:
        return self._generate_questions_from_brave(subject, [topic], num_questions)

    def _generate_questions_from_brave(self, subject: str, topics: list[str], num_questions: int = 10) -> dict:
        """Search Brave for real exam questions, then use AI only to structure/parse into JSON."""

        queries = [
            f"JAMB {subject} past questions and answers multiple choice",
            f"WAEC {subject} past questions and answers options A B C D",
            f"NECO {subject} examination past questions",
        ]
        for t in topics[:2]:
            queries.append(f"JAMB {subject} {t} past questions")

        all_results = []
        for q in queries:
            if len(all_results) >= 40:
                break
            results = self._brave_search(q, count=8)
            all_results.extend(results)

        if not all_results:
            for t in topics[:3]:
                results = self._brave_search(f"{subject} {t} exam questions options", count=8)
                all_results.extend(results)
                if len(all_results) >= 20:
                    break

        if not all_results:
            return {"questions": []}

        search_text = "\n\n---\n\n".join([
            f"Source {i+1}: {r['title']}\nURL: {r.get('url', '')}\nContent: {r['snippet']}"
            for i, r in enumerate(all_results)
        ])
        if len(search_text) > 30000:
            search_text = search_text[:30000] + "..."

        topic_list = ", ".join(topics)
        prompt = f"""Below are web search results containing real exam questions about {subject}.

Your ONLY task: Extract actual multiple-choice questions from the search results above.
CRITICAL: Do NOT generate, create, or invent any new questions. Only extract questions that are clearly present in the provided text.

For each extracted question, output:
- text: The exact question text
- options: Array of 4 options like ["A) option1", "B) option2", "C) option3", "D) option4"]
- correct_answer: The correct option letter (A, B, C, or D). If the answer is not clear from the text, put "unknown"
- explanation: A brief explanation or cite the source
- difficulty: "easy", "medium", or "hard"
- topic: Which topic this fits best — choose from: {topic_list}

{search_text}

Return ONLY valid JSON:
{{"questions": [{{"text": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "correct_answer": "A", "explanation": "...", "difficulty": "medium", "topic": "..."}}]}}"""

        messages = [
            {"role": "system", "content": "You extract real exam questions from web search results and format them as JSON. Never generate new questions."},
            {"role": "user", "content": prompt}
        ]

        response = self._call_openai(messages, temperature=0.3, max_tokens=4000)
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])

        try:
            data = json.loads(response)
            questions = data.get("questions", [])
        except json.JSONDecodeError:
            questions = []

        if questions:
            return {"questions": questions[:num_questions]}
        return {"questions": []}

    def generate_quiz(self, subject: str, topic: str, difficulty: str = "medium", num_questions: int = 5) -> dict:
        prompt = f"""Generate {num_questions} multiple-choice questions about {topic} in {subject} for Nigerian secondary school students preparing for WAEC, NECO, and JAMB examinations.

DIFFICULTY: {difficulty}

Each question must:
- Test deep understanding, not surface recall
- Include plausible distractors based on common student mistakes
- Be exam-standard quality
- Include a detailed explanation

Return ONLY valid JSON in this exact format:
{{
  "title": "Quiz on {topic}",
  "questions": [
    {{
      "text": "Question text",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A",
      "explanation": "Why this answer is correct and why others are wrong",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}"""

        messages = [
            {"role": "system", "content": "You are a Nigerian exam question generator. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]

        response = self._call_openai(messages, temperature=0.8)
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])

        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError:
            return {
                "title": f"Quiz on {topic}",
                "questions": []
            }

    def generate_textbook_content(self, subject: str, topic: str, existing_content: str = "") -> str:
        ref = existing_content[:500] if existing_content else "No existing content — write from scratch."

        part1_prompt = f"""You are writing PART 1 of a comprehensive textbook chapter on "{topic}" for {subject} (WAEC/NECO/JAMB).

This is PART 1 of 3. Focus on: Fundamentals, Core Concepts, and Introduction.

Structure with HTML:
<h2>Learning Objectives</h2> — 10-15 specific objectives
<h2>Introduction</h2> — Real-world relevance, define the topic
<h2>Section 1: Fundamental Concepts</h2> — Start from basics, define every term. 5+ worked examples with FULL step-by-step solutions
<h2>Section 2: Core Principles</h2> — Deep dive into principles, derivations. 6+ worked examples covering different scenarios. Include common misconceptions

FORMATTING: Use HTML (h2/h3/h4, p with strong for key terms, pre/code for formulas, ul/ol, tables for comparisons). Every example must have: Problem, Step-by-step solution, Final answer.

Reference: {ref}

Write PART 1 now — maximum detail (~7,000 tokens)."""

        part2_prompt = f"""You are writing PART 2 of a comprehensive textbook chapter on "{topic}" for {subject} (WAEC/NECO/JAMB).

This is PART 2 of 3. Focus on: Advanced Applications, Problem-Solving, and Real-World Context.

Structure with HTML:
<h2>Section 3: Applications and Problem-Solving</h2> — Real-world Nigerian context applications. 10+ exam-style problems with full solutions. Show alternative methods
<h2>Section 4: Advanced Topics</h2> — Complex aspects. 5+ challenging problems with solutions. Connect to other syllabus topics

FORMATTING: Use HTML (h2/h3/h4, p with strong, pre/code, ul/ol, tables). Every example must have: Problem, Step-by-step solution, Final answer.

Reference: {ref}

Write PART 2 now — maximum detail (~7,000 tokens)."""

        part3_prompt = f"""You are writing PART 3 of a comprehensive textbook chapter on "{topic}" for {subject} (WAEC/NECO/JAMB).

This is PART 3 of 3. Focus on: Exam Preparation and Practice.

Structure with HTML:
<h2>Section 5: Exam Preparation</h2> — How JAMB/WAEC tests this topic. Common question patterns. Time-saving techniques. 10+ practice questions with answers
<h2>Summary</h2> — Key formulas, concepts, takeaways
<h2>Practice Exercises (with Answers)</h2> — 20+ exercises from easy to difficult. Full answers and brief solutions
<h2>Further Reading</h2> — Related topics to study next

FORMATTING: Use HTML (h2/h3/h4, p with strong, pre/code, ul/ol, tables). Every exercise must have: Question, Answer, Brief solution.

Reference: {ref}

Write PART 3 now — maximum detail (~7,000 tokens)."""

        parts = []
        prompts = [part1_prompt, part2_prompt, part3_prompt]
        for i, prompt in enumerate(prompts, 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a Nigerian textbook author writing for WAEC/NECO/JAMB students. Write in extremely detailed HTML."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=7000
                )
                content = response.choices[0].message.content or ""
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1])
                parts.append(content)
                logger.info(f"Textbook Part {i}/3 generated ({len(content)} chars)")
            except Exception as e:
                logger.error(f"Failed to generate textbook Part {i}: {e}")
                parts.append(f"<p>Part {i} could not be generated due to a temporary error. Please try again.</p>")

        full_content = "\n<hr class=\"part-divider\">\n".join(parts)
        return full_content

    async def _call_openai_async(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4000) -> str:
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise ValueError("AI service authentication failed. Please check the API key.")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}")
            raise ValueError("AI service is currently busy. Please try again in a moment.")
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI timeout error: {e}")
            raise ValueError("AI service timed out. Please try again.")
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}")
            raise ValueError("Could not connect to AI service. Please check your internet connection.")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError("AI service encountered an error. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}")
            raise ValueError("An unexpected error occurred. Please try again.")

    async def _brave_search_async(self, query: str, count: int = 10) -> list[dict]:
        if not self.brave_api_key:
            logger.warning("No Brave API key configured")
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": count},
                    headers={"X-Subscription-Token": self.brave_api_key},
                )
                resp.raise_for_status()
                data = resp.json()
                results = []
                for item in data.get("web", {}).get("results", []):
                    desc = item.get("description", "") or ""
                    title = item.get("title", "") or ""
                    results.append({"title": title, "snippet": desc, "url": item.get("url", "")})
                    if item.get("extra_snippets"):
                        for s in item["extra_snippets"]:
                            results.append({"title": title, "snippet": s, "url": item.get("url", "")})
                return results
        except Exception as e:
            logger.error(f"Async Brave search failed: {e}")
            return []

    async def generate_section(self, prompt: str, section_index: int) -> str:
        system = """You are a Nigerian textbook author writing for WAEC/NECO/JAMB/GCE/Post-UTME students.

CRITICAL: All mathematical expressions MUST use plain text notation ONLY.
- Never use LaTeX. Never use $...$ or $$...$$.
- Use 'x^2' for exponents, 'a/b' for fractions, 'sqrt(x)' for square roots.
- Write formulas clearly in plain text like: E = mc^2, F = ma, x = (-b +/- sqrt(b^2 - 4ac)) / 2a
- Use words like 'integral', 'sum', 'delta' instead of symbols.
- For subscripts, write x_1 or x(subscript 1).

Write detailed HTML content with worked examples, step-by-step solutions, and exam-level explanations."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        content = await self._call_openai_async(messages, temperature=0.7, max_tokens=4000)
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        return content

    async def generate_exam_questions_for_topic(
        self,
        subject: str,
        exam_type: str,
        topic: str,
        num_questions: int = 10,
        skip_search: bool = False,
    ) -> list[dict]:
        """Generate exam questions using AI with optional Brave Search enrichment."""

        extract_section = ""
        if not skip_search:
            queries = [
                f"{exam_type} {subject} {topic} past questions answers",
                f"{exam_type} {subject} difficult questions {topic}",
                f"{subject} {topic} examination questions and answers",
            ]
            all_results = []
            for q in queries:
                if len(all_results) >= 30:
                    break
                results = await self._brave_search_async(q, count=8)
                all_results.extend(results)

            search_text = ""
            if all_results:
                search_text = "\n\n---\n\n".join([
                    f"Source {i+1}: {r['title']}\nURL: {r.get('url', '')}\nContent: {r['snippet']}"
                    for i, r in enumerate(all_results)
                ])
                if len(search_text) > 25000:
                    search_text = search_text[:25000] + "..."

            if search_text:
                extract_section = f"""
Below are web search results with real exam questions. Extract any real questions found:
{search_text}

---
"""

        prompt = f"""Generate {num_questions} multiple-choice questions about "{topic}" in {subject} for {exam_type} examination.

Each question must:
- Test real understanding, not recall
- Have 4 plausible options where wrong ones are common mistakes
- Include a step-by-step explanation
- Use plain text for formulas (x^2, sqrt(x), a/b)

Return ONLY valid JSON:
{{"questions": [{{"text":"...","options":["A) ...","B) ...","C) ...","D) ..."],"correct_answer":"A","explanation":"...","difficulty":"medium","topic":"{topic}"}}]}}"""

        messages = [
            {"role": "system", "content": "You are a WAEC/JAMB examiner. Generate questions that test understanding. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]

        response = await self._call_openai_async(messages, temperature=0.7, max_tokens=3000)
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])

        try:
            data = json.loads(response)
            return data.get("questions", [])[:num_questions]
        except json.JSONDecodeError:
            logger.error(f"Failed to parse generated exam questions JSON, raw: {response[:200]}")
            return []

    def generate_exam_questions_sync(
        self,
        subject: str,
        exam_type: str,
        topic: str,
        num_questions: int = 10,
    ) -> list[dict]:
        """Synchronous, no-Brave-search question generation for parallel use."""
        prompt = f"""You are a JAMB chief examiner for {subject}. Generate {num_questions} extremely difficult multiple-choice questions.

COVERAGE: Pull questions from across the ENTIRE {subject} syllabus — mix topics, don't focus on one area. Connect 2-3 different concepts in each question.

DIFFICULTY RULES:
- Require 3+ step reasoning — never test a single fact
- Each question must have a "trap" answer that looks obviously correct but is wrong
- Include distractors that match specific common student mistakes
- Frame as multi-layered scenarios, calculations, or experiments
- Use "always/never/only/except/all of the above except" for precision traps
- Calculations must need unit conversions or hidden conditions

MATH FORMAT: Use plain text (x^2, sqrt(x), x/y) — NO LaTeX.

Return ONLY JSON:
{{"questions":[
  {{"text":"...","options":["A) ...","B) ...","C) ...","D) ..."],"correct_answer":"A","explanation":"Why right + why each distractor is wrong","difficulty":"very_hard","topic":"mixed"}}
]}}"""

        messages = [
            {"role": "system", "content": f"You are the toughest JAMB chief examiner. Your questions make top students cry. Every question must have a deadly trap. Connect multiple syllabus topics per question. Plain text math only."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self._call_openai(messages, temperature=0.7, max_tokens=2500)
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            data = json.loads(response)
            return data.get("questions", [])[:num_questions]
        except Exception:
            return []

    def generate_study_plan(self, subjects: list[str], duration_days: int) -> list[dict]:
        prompt = f"""Create a {duration_days}-day study plan for Nigerian secondary school students preparing for WAEC, NECO, and JAMB examinations.

Subjects: {', '.join(subjects)}

Design a realistic, structured plan that covers the syllabus efficiently.

Return ONLY valid JSON as an array of day objects:
[
  {{
    "day": 1,
    "subjects": ["Mathematics"],
    "topics": ["Algebra basics"],
    "duration_minutes": 120,
    "activities": ["Review notes", "Practice problems"],
    "resources": ["Textbook chapter 3"]
  }}
]"""

        messages = [
            {"role": "system", "content": "You are a study planner for Nigerian exams. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]

        response = self._call_openai(messages, temperature=0.7)
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [
                {
                    "day": 1,
                    "subjects": [subjects[0] if subjects else "General"],
                    "topics": ["Introduction"],
                    "duration_minutes": 120,
                    "activities": ["Study core concepts"],
                    "resources": ["Recommended textbooks"]
                }
            ]
