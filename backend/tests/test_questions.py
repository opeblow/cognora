"""Quick test: hit the quiz generation endpoint / api directly."""
import asyncio, json, logging
logging.basicConfig(level=logging.ERROR)

from app.core.config import settings
from app.services.ai_service import AIService

async def main():
    ai = AIService()
    print(f"Model: {settings.OPENAI_MODEL}")
    print(f"API Key set: {bool(settings.OPENAI_API_KEY)}")
    
    # Test 1: simple generation (skip_search=True)
    print("\n=== Test 1: AI-only question generation ===")
    result = await ai.generate_exam_questions_for_topic(
        subject="Mathematics",
        exam_type="WAEC/JAMB",
        topic="Algebra",
        num_questions=10,
        skip_search=True
    )
    print(f"Got {len(result)} questions")
    for q in result:
        print(f"  Q: {q.get('text','')[:60]}")
        print(f"  Options: {q.get('options',[])}")
        print(f"  Answer: {q.get('correct_answer','')}")
        print()
    
    if len(result) >= 5:
        print("PASS: >= 5 questions generated")
    else:
        print("FAIL: not enough questions")

if __name__ == "__main__":
    asyncio.run(main())
