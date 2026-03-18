from app.core.config import settings
from app.schemas.llm_job_parser import LLMParsedJobResponse
from app.services.gemini_client import get_gemini_client


def parse_job_description_with_llm(
    title: str | None,
    company: str | None,
    location: str | None,
    description: str,
) -> dict:
    client = get_gemini_client()

    prompt = f"""
You are an expert job description parser for the German and European tech job market.

Extract structured information from this job description.

Rules:
- Return clean normalized values.
- skills should be concrete technical or role-relevant skills.
- keywords should include important ATS-relevant terms.
- work_model should be one of: remote, hybrid, onsite, or null.
- employment_type should be one of: full-time, part-time, contract, internship, or null.
- seniority should be one of: intern, junior, mid, senior, lead, or null.
- summary should be a concise 2-4 sentence summary of the role.
- If a field is not clearly available, return null or false or [] as appropriate.

Input metadata:
title: {title}
company: {company}
location: {location}

Job description:
{description}
""".strip()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": LLMParsedJobResponse,
        },
    )

    parsed = response.parsed
    if parsed is None:
        raise ValueError("Gemini returned no parsed structured output")

    return parsed.model_dump()