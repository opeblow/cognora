import random
import json
import hashlib
import logging
import asyncio
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

BOARDS = ["WAEC", "NECO", "GCE", "JAMB"]

SUBJECTS_BY_BOARD = {
    "WAEC": [
        "Mathematics", "English Language", "Civic Education",
        "Physics", "Chemistry", "Biology",
        "Economics", "Government", "Literature in English",
        "Computer Studies", "Agricultural Science",
    ],
    "NECO": [
        "Mathematics", "English Language", "Civic Education",
        "Physics", "Chemistry", "Biology",
        "Economics", "Government", "Literature in English",
        "Computer Studies", "Agricultural Science",
    ],
    "GCE": [
        "Mathematics", "English Language", "Civic Education",
        "Physics", "Chemistry", "Biology",
        "Economics", "Government", "Literature in English",
        "Computer Studies", "Agricultural Science",
    ],
    "JAMB": [
        "Mathematics", "English Language",
        "Physics", "Chemistry", "Biology",
        "Economics", "Government", "Literature in English",
        "Computer Studies", "Agricultural Science",
        "CRS", "Islamic Studies", "Yoruba", "Igbo", "Hausa",
    ],
}

YEARS_BY_BOARD = {
    "WAEC": list(range(2025, 1951, -1)),
    "JAMB": list(range(2025, 1977, -1)),
    "NECO": list(range(2025, 1999, -1)),
    "GCE": list(range(2025, 1951, -1)),
}

# Cache TTLs
SEARCH_CACHE_TTL = 3600       # 1 hour — Brave search results
PAGE_CACHE_TTL = 7200         # 2 hours — fetched page content
QUESTIONS_CACHE_TTL = 1800    # 30 min — parsed questions per board/subject/year


class PastQuestionService:
    def __init__(self):
        self.brave_api_key = settings.BRAVE_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self._http_client = None
        self._async_http_client = None
        self._openai_client = None

    @property
    def http_client(self):
        import httpx
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.Client(timeout=10.0)
        return self._http_client

    @property
    def async_http_client(self):
        import httpx
        if self._async_http_client is None or self._async_http_client.is_closed:
            self._async_http_client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
        return self._async_http_client

    @property
    def openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=self.openai_api_key, timeout=60.0)
        return self._openai_client

    def _get_redis(self):
        try:
            from app.database.redis import get_redis
            return get_redis()
        except Exception:
            return None

    def _cache_key(self, prefix: str, *args) -> str:
        raw = f"{prefix}:{':'.join(str(a) for a in args)}"
        return f"past_q:{hashlib.md5(raw.encode()).hexdigest()}"

    async def _get_cached(self, key: str) -> Optional[dict]:
        redis = self._get_redis()
        if redis is None:
            return None
        try:
            import pickle
            data = await redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception:
            pass
        return None

    async def _set_cached(self, key: str, value: dict, ttl: int):
        redis = self._get_redis()
        if redis is None:
            return
        try:
            import pickle
            await redis.setex(key, ttl, pickle.dumps(value))
        except Exception:
            pass

    async def _brave_search_async(self, query: str, count: int = 10) -> list[dict]:
        cache_key = self._cache_key("brave", query, count)
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self.brave_api_key:
            return []
        try:
            resp = await self.async_http_client.get(
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
            await self._set_cached(cache_key, results, SEARCH_CACHE_TTL)
            return results
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []

    async def _fetch_page_async(self, url: str) -> str:
        cache_key = self._cache_key("page", url)
        cached = await self._get_cached(cache_key)
        if cached is not None:
            return cached.get("content", "")

        try:
            resp = await self.async_http_client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            if resp.status_code == 200:
                text = resp.text[:15000]
                await self._set_cached(cache_key, {"content": text}, PAGE_CACHE_TTL)
                return text
            return ""
        except Exception:
            return ""

    def get_filter_options(self) -> dict:
        return {"boards": BOARDS, "years": {}}

    def get_subjects_for_board(self, board: str) -> list[str]:
        return SUBJECTS_BY_BOARD.get(board, [])

    def get_years_for_board(self, board: str) -> list[int]:
        return YEARS_BY_BOARD.get(board, list(range(2025, 2000, -1)))

    async def _start_practice_async(self, board: str, subject: str, year: int, count: int) -> dict:
        q_key = self._cache_key("questions", board, subject, year)
        cached_questions = await self._get_cached(q_key)
        if cached_questions and len(cached_questions) >= count:
            selected = random.sample(cached_questions, min(count, len(cached_questions)))
            return {
                "questions": selected,
                "total": len(selected),
                "board": board,
                "subject": subject,
                "year": year,
            }

        queries = [
            f"{year} {board} {subject} past questions and answers multiple choice",
            f"{board} {subject} {year} examination questions options A B C D",
            f"{board} {subject} {year} past paper questions",
        ]

        search_results = await asyncio.gather(
            *[self._brave_search_async(q, count=10) for q in queries],
            return_exceptions=True,
        )
        all_results = []
        for r in search_results:
            if isinstance(r, list):
                all_results.extend(r)
        if len(all_results) > 30:
            all_results = all_results[:30]

        seen_urls = set()
        urls_to_fetch = []
        for r in all_results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                urls_to_fetch.append(url)
            if len(urls_to_fetch) >= 5:
                break

        page_results = await asyncio.gather(
            *[self._fetch_page_async(url) for url in urls_to_fetch],
            return_exceptions=True,
        )
        fetched_content = []
        for url, content in zip(urls_to_fetch, page_results):
            if isinstance(content, str) and content:
                fetched_content.append({"url": url, "content": content})

        source_text = ""
        for i, r in enumerate(all_results[:30]):
            source_text += f"Source {i+1}: {r['title']}\nURL: {r.get('url', '')}\nSnippet: {r['snippet']}\n\n"
        if len(source_text) > 20000:
            source_text = source_text[:20000] + "..."

        page_text = ""
        for item in fetched_content:
            page_text += f"\n--- Page: {item['url']} ---\n{item['content']}\n"
        if len(page_text) > 30000:
            page_text = page_text[:30000] + "..."

        combined = f"SEARCH RESULTS:\n{source_text}"
        if page_text:
            combined += f"\n\nFULL PAGE CONTENT:\n{page_text}"

        prompt = f"""Below are web search results and page content containing real {board} {subject} past questions for {year}.

CRITICAL RULES:
1. Extract ONLY real multiple-choice questions that actually appear in the text above
2. Do NOT invent, create, or fabricate any questions
3. Each question must have exactly 4 options (A, B, C, D)
4. Include the correct answer for each question
5. If you can determine the topic/subtopic, include it
6. If you cannot determine the correct answer, set correct_answer to "unknown"
7. Clean up the question text — remove artifacts, numbering, broken formatting
8. If there are fewer than {count} real questions in the text, return fewer — quality over quantity

Return ONLY valid JSON (no markdown, no explanation):
{{"questions": [{{"text": "Question text here", "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"], "correct_answer": "A", "explanation": "Brief explanation", "difficulty": "medium", "topic": "Subtopic name"}}]}}"""

        messages = [
            {"role": "system", "content": f"You are a {board} exam question extractor. You extract real past questions from web content and format them as JSON. You never invent questions. Return ONLY valid JSON."},
            {"role": "user", "content": prompt},
        ]

        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=0.3,
            max_tokens=4000,
        )
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1])

        try:
            data = json.loads(raw)
            questions = data.get("questions", [])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {raw[:200]}")
            return {"questions": [], "source": "AI parsing failed", "total": 0, "board": board, "subject": subject, "year": year}

        cleaned = []
        seen_texts = set()
        for q in questions:
            text = (q.get("text") or "").strip()
            options = q.get("options", [])
            if len(text) < 10 or len(options) < 2:
                continue
            q_key_text = text[:80].lower()
            if q_key_text in seen_texts:
                continue
            seen_texts.add(q_key_text)
            if len(options) == 4:
                random.shuffle(options)
            cleaned.append({
                "id": f"pq_{hash(text)}",
                "question": text,
                "options": options,
                "correct_answer": q.get("correct_answer", "unknown"),
                "explanation": q.get("explanation", ""),
                "difficulty": q.get("difficulty", "medium"),
                "topic": q.get("topic", ""),
            })

        if cleaned:
            await self._set_cached(q_key, cleaned, QUESTIONS_CACHE_TTL)

        random.shuffle(cleaned)
        selected = cleaned[:count]

        return {
            "questions": selected,
            "total": len(selected),
            "board": board,
            "subject": subject,
            "year": year,
        }

    def start_practice(self, board: str, subject: str, year: int, count: int = 20) -> dict:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._start_practice_async(board, subject, year, count))
                    return future.result(timeout=120)
            else:
                return loop.run_until_complete(self._start_practice_async(board, subject, year, count))
        except RuntimeError:
            return asyncio.run(self._start_practice_async(board, subject, year, count))

    def submit_practice(self, questions: list[dict], answers: dict) -> dict:
        results = []
        score = 0
        for q in questions:
            qid = q.get("id", "")
            selected = answers.get(qid, "")
            correct = q.get("correct_answer", "unknown")
            is_correct = selected.strip().upper() == correct.strip().upper() if correct != "unknown" else False
            if is_correct:
                score += 1
            results.append({
                "question_id": qid,
                "question": q.get("question", ""),
                "selected_answer": selected,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": q.get("explanation", ""),
                "options": q.get("options", []),
            })
        total = len(questions)
        percentage = (score / total * 100) if total > 0 else 0
        return {
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
            "results": results,
        }
