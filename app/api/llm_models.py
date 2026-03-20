from typing import List

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.services.gemini_client import get_gemini_client
from app.services.llm_text import (
    _list_available_generation_models,
    PREFERRED_GEMINI_MODELS,
    generate_text,
)

try:
    from google.api_core.exceptions import Forbidden, PermissionDenied
except ImportError:  # pragma: no cover
    Forbidden = Exception  # type: ignore[assignment]
    PermissionDenied = Exception  # type: ignore[assignment]

router = APIRouter(prefix="/llm-models", tags=["llm-models"])


@router.get("", response_model=List[str])
def list_llm_models() -> List[str]:
    """List Gemini models that appear to support text generation."""

    try:
        client = get_gemini_client()
        return _list_available_generation_models(client)

    except (Forbidden, PermissionDenied):
        # Some API keys cannot list available models (permission issue).
        # Fall back to a known-safe list so callers can still choose a model.
        return PREFERRED_GEMINI_MODELS.copy()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to list Gemini models: {exc}. "
                f"Try setting GEMINI_MODEL to one of: {', '.join(PREFERRED_GEMINI_MODELS)}."
            ),
        )


@router.get("/validate")
def validate_current_model():
    """Validate the currently configured GEMINI_MODEL by making a small test generation."""

    try:
        out = generate_text("Please respond with the word OK.")
        return {
            "configured_model": settings.GEMINI_MODEL,
            "success": True,
            "output": out,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Model validation failed for {settings.GEMINI_MODEL}: {exc}. "
                f"Try setting GEMINI_MODEL to one of: {', '.join(PREFERRED_GEMINI_MODELS)}."
            ),
        )
