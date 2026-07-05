import logging
from pathlib import Path
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class AudioService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)
        self.whisper_model = settings.WHISPER_MODEL
        self.llm_model = settings.OPENAI_MODEL

    def transcribe(self, file_path: str) -> str:
        with open(file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                response_format="text",
            )
        logger.info(f"Transcribed audio ({len(transcript)} chars)")
        return transcript.strip()

    def generate_feedback(
        self, transcript: str, subject: str | None = None, topic: str | None = None
    ) -> str:
        system = (
            "You are Cognora AI, an expert tutor for Nigerian secondary school students "
            "preparing for WAEC, NECO, GCE, JAMB, and Post-UTME examinations."
        )

        context = ""
        if subject:
            context += f"\nSubject: {subject}"
        if topic:
            context += f"\nTopic: {topic}"

        prompt = (
            f"The student has submitted the following voice recording transcript:{context}\n\n"
            f"TRANSCRIPT:\n{transcript}\n\n"
            "Provide helpful pedagogical feedback:\n"
            "1. If the student asked a question, answer it clearly with examples.\n"
            "2. If the student is explaining a concept, correct any errors and fill gaps.\n"
            "3. If the student is practicing, give constructive feedback on their understanding.\n"
            "4. Always encourage and suggest next steps for study.\n\n"
            "Keep your response clear, structured, and encouraging. Use plain text."
        )

        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        feedback = response.choices[0].message.content or ""
        logger.info(f"Generated feedback ({len(feedback)} chars)")
        return feedback.strip()
