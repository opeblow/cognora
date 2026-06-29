from app.core.config import settings
from typing import Optional
import json


class AIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def _call_openai(self, messages: list[dict], temperature: float = 0.7) -> str:
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=2000
        )
        return response.choices[0].message.content

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

Keep responses structured and engaging. Use markdown for formatting."""

        if subject:
            system_prompt += f"\nCurrent subject: {subject}"

        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.extend(context[-10:])
        messages.append({"role": "user", "content": message})

        response = self._call_openai(messages)
        return {"response": response, "suggestions": []}

    def generate_quiz(self, subject: str, topic: str, difficulty: str = "medium", num_questions: int = 5) -> dict:
        prompt = f"""Generate {num_questions} multiple-choice questions about {topic} in {subject} for Nigerian secondary school students.

Difficulty level: {difficulty}
Exam target: WAEC/NECO/JAMB

Return ONLY valid JSON in this exact format:
{{
  "title": "Quiz title here",
  "questions": [
    {{
      "text": "Question text",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A",
      "explanation": "Why this answer is correct",
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
                "questions": [
                    {
                        "text": f"Sample question about {topic}?",
                        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                        "correct_answer": "A",
                        "explanation": f"Explanation for the {topic} question."
                    }
                ]
            }

    def generate_study_plan(self, subjects: list[str], duration_days: int) -> list[dict]:
        prompt = f"""Create a {duration_days}-day study plan for Nigerian secondary school students.

Subjects: {', '.join(subjects)}
Target exams: WAEC, NECO, JAMB

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
