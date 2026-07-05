import base64
import logging
import mimetypes
from pathlib import Path
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class OcrService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)

    def extract_text(self, file_path: str, mime_type: str) -> str:
        if mime_type == "application/pdf":
            return self._extract_from_pdf(file_path)
        elif mime_type.startswith("image/"):
            return self._extract_from_image(file_path, mime_type)
        else:
            raise ValueError(f"Unsupported mime type for OCR: {mime_type}")

    def _extract_from_pdf(self, file_path: str) -> str:
        try:
            import fitz
            doc = fitz.open(file_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            full_text = "\n".join(text_parts).strip()
            if full_text:
                logger.info(f"Extracted {len(full_text)} chars via PyMuPDF")
                return full_text
        except ImportError:
            logger.info("PyMuPDF not available, falling back to vision-based PDF OCR")
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")

        return self._extract_from_image(file_path, "image/png")

    def _extract_from_image(self, file_path: str, mime_type: str) -> str:
        image_ext = Path(file_path).suffix.lower().lstrip(".")
        if image_ext in ("jpg", "jpeg"):
            fmt = "jpeg"
        elif image_ext == "png":
            fmt = "png"
        elif image_ext == "webp":
            fmt = "webp"
        else:
            fmt = "png"

        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        data_url = f"data:image/{fmt};base64,{b64_data}"

        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract ALL text from this document image. "
                                "Return the text exactly as written, preserving the original structure, "
                                "paragraphs, and formatting where possible. "
                                "If there are tables, format them using markdown table syntax. "
                                "If there are mathematical formulas, write them in plain text notation."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=4096,
        )

        text = response.choices[0].message.content or ""
        logger.info(f"Extracted {len(text)} chars via OpenAI Vision")
        return text.strip()
