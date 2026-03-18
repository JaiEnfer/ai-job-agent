from google import genai
from app.core.config import settings


def get_gemini_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    return genai.Client(api_key=settings.GEMINI_API_KEY)