from google import genai
from app.core.config import settings


def get_gemini_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    # The Gemini developer API is the default. Some users may instead need Vertex AI.
    # Vertex AI requires a project and a location (e.g., us-central1).
    if settings.GEMINI_USE_VERTEXAI:
        if not settings.GEMINI_VERTEXAI_PROJECT or not settings.GEMINI_VERTEXAI_LOCATION:
            raise ValueError(
                "GEMINI_USE_VERTEXAI is true, but GEMINI_VERTEXAI_PROJECT or GEMINI_VERTEXAI_LOCATION is not set"
            )
        return genai.Client(
            api_key=settings.GEMINI_API_KEY,
            vertexai=True,
            project=settings.GEMINI_VERTEXAI_PROJECT,
            location=settings.GEMINI_VERTEXAI_LOCATION,
        )

    return genai.Client(api_key=settings.GEMINI_API_KEY)