import re
import logging
from typing import Literal
from dataclasses import dataclass, field

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

ClaimStatus = Literal["confirmed", "partial", "contradicted", "unverifiable"]


@dataclass
class Verdict:
    claim: str
    status: ClaimStatus
    sources: list[str] = field(default_factory=list)
    confidence: float = 0.0


class GroundingService:
    def __init__(self):
        self.api_key = settings.BRAVE_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def verify_question(self, question_text: str, correct_answer: str) -> list[dict]:
        claims = self._extract_claims(f"{question_text} {correct_answer}")
        verdicts = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for claim in claims[:5]:
                verdict = await self._verify_single_claim(client, claim)
                verdicts.append({
                    "claim": verdict.claim,
                    "status": verdict.status,
                    "sources": verdict.sources,
                    "confidence": verdict.confidence,
                })

        return verdicts

    def _extract_claims(self, text: str) -> list[str]:
        claims = []

        years = re.findall(r'\b(?:19|20)\d{2}\b', text)
        claims.extend([f"year {y}" for y in years])

        entities = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', text)
        claims.extend([e for e in entities if len(e) > 3])

        measurements = re.findall(r'\b\d+\.?\d*\s*(?:km|m|kg|g|N|J|V|A|Hz|%|°C|cm|mm|L|ml|s|h)\b', text)
        claims.extend(measurements)

        definitions = re.findall(r'([A-Za-z\s]{3,50})\s+is\s+(?:the\s+|a\s+|an\s+)?([A-Za-z\s]{3,100}?)(?:\.|,|;)', text)
        claims.extend([f"{d[0].strip()} definition" for d in definitions])

        return list(set(claims))

    async def _verify_single_claim(self, client: httpx.AsyncClient, claim: str) -> Verdict:
        if not self.api_key:
            return Verdict(claim=claim, status="unverifiable")

        query = f'"{claim}" educational OR textbook OR curriculum'
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }

        try:
            response = await client.get(
                self.base_url,
                params={"q": query, "count": 3, "freshness": "py"},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.warning(f"Brave search failed for claim '{claim}': {e}")
            return Verdict(claim=claim, status="unverifiable")

        web_results = data.get("web", {}).get("results", [])
        if not web_results:
            return Verdict(claim=claim, status="unverifiable")

        supporting = []
        claim_lower = claim.lower()
        for r in web_results:
            snippet = (r.get("title", "") + " " + r.get("description", "")).lower()
            if claim_lower in snippet:
                supporting.append(r.get("url", ""))

        if len(supporting) >= 2:
            status = "confirmed"
        elif len(supporting) == 1:
            status = "partial"
        else:
            contradicting = False
            for r in web_results:
                snippet = (r.get("title", "") + " " + r.get("description", "")).lower()
                for neg in ["not", "incorrect", "false", "disputed", "myth", "wrong", "debunked"]:
                    if neg in snippet and claim.split()[0].lower() in snippet:
                        contradicting = True
                        break
            status = "contradicted" if contradicting else "unverifiable"

        score = len(supporting) / max(len(web_results), 1)
        return Verdict(claim=claim, status=status, sources=supporting, confidence=round(score, 2))
