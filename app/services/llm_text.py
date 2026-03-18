from app.core.config import settings
from app.services.gemini_client import get_gemini_client


def generate_text(prompt: str) -> str:
    client = get_gemini_client()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    return (response.text or "").strip()