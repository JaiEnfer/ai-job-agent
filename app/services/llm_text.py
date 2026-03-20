from __future__ import annotations

from app.core.config import settings
from app.services.gemini_client import get_gemini_client


try:
    from google.api_core.exceptions import InvalidArgument, NotFound
except ImportError:  # pragma: no cover
    InvalidArgument = Exception  # type: ignore[assignment]
    NotFound = Exception  # type: ignore[assignment]


def _supports_generation(model) -> bool:
    """Return True if the model appears to support content generation."""

    supported_actions = getattr(model, "supported_actions", None) or []
    if not supported_actions:
        return False

    for action in supported_actions:
        try:
            action_text = str(action).lower()
        except Exception:
            continue
        if "generat" in action_text:
            return True

    return False


PREFERRED_GEMINI_MODELS: list[str] = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-lite",
]


def _list_available_generation_models(client) -> list[str]:
    """Return a short list of models that appear to support generate_content."""

    try:
        models = list(client.models.list(config={"page_size": 50}))
    except Exception:
        # In environments where the API key cannot list models (403/Forbidden),
        # fall back to a small hard-coded list of commonly available Gemini models.
        return PREFERRED_GEMINI_MODELS.copy()

    candidates: list[str] = []
    for m in models:
        if _supports_generation(m):
            name = getattr(m, "name", None) or getattr(m, "display_name", None)
            if name:
                candidates.append(str(name))

    return candidates[:10] or PREFERRED_GEMINI_MODELS.copy()


def _choose_fallback_model(client, attempted_model: str) -> str | None:
    # Prefer a few known Gemini models that typically support generation.
    preferred = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-lite",
    ]

    available = _list_available_generation_models(client)
    for pref in preferred:
        if pref in available:
            return pref

    return available[0] if available else None


def generate_text(prompt: str) -> str:
    client = get_gemini_client()
    model = settings.GEMINI_MODEL

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return (response.text or "").strip()

    except Exception as exc:
        # If the model is not available (404) or unsupported for generate_content, try a series of fallbacks.
        is_unavailable = isinstance(exc, (NotFound, InvalidArgument))
        if not is_unavailable:
            msg = str(exc).lower()
            is_unavailable = "not found" in msg or "not supported" in msg or ("model" in msg and "not" in msg)

        if not is_unavailable:
            raise RuntimeError(f"LLM generation failed (model={model}): {exc}") from exc

        # Generate a prioritized list of candidates to try.
        candidates = [model] + _list_available_generation_models(client)
        # Deduplicate while preserving order.
        seen: set[str] = set()
        deduped: list[str] = []
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            deduped.append(candidate)

        last_error = exc
        for candidate in deduped[1:]:
            try:
                response = client.models.generate_content(
                    model=candidate,
                    contents=prompt,
                )
                return (response.text or "").strip()
            except Exception as try_exc:
                last_error = try_exc

        available_models = ", ".join(deduped[:5]) or "(none available)"

        message = (
            f"LLM model '{model}' is not available (or not supported for generateContent). "
            f"Tried candidates: {available_models}. "
        )

        if not settings.GEMINI_USE_VERTEXAI and "v1beta" in str(last_error).lower():
            message += (
                "It looks like your key is hitting the Gemini Developer API (v1beta). "
                "If you are using a Google Cloud (Vertex AI) API key, set "
                "GEMINI_USE_VERTEXAI=true and configure GEMINI_VERTEXAI_PROJECT/LOCATION, "
                "then use a Vertex model like 'text-bison-001'. "
            )

        message += f"Last error: {last_error}"
        raise RuntimeError(message) from last_error
