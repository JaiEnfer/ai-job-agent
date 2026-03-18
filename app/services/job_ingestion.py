import re
from typing import Optional


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned if cleaned else None


def infer_title_from_description(description: str) -> Optional[str]:
    if not description:
        return None

    lines = [line.strip() for line in description.splitlines() if line.strip()]
    if not lines:
        return None

    first_line = lines[0]

    if len(first_line) <= 120:
        return first_line

    return None


def infer_company_from_description(description: str) -> Optional[str]:
    if not description:
        return None

    patterns = [
        r"(?i)\bjoin\s+([A-Z][A-Za-z0-9&\-\.\s]{2,50})",
        r"(?i)\bat\s+([A-Z][A-Za-z0-9&\-\.\s]{2,50})",
    ]

    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            candidate = clean_text(match.group(1))
            if candidate and len(candidate) <= 60:
                return candidate

    return None


def normalize_job_payload(
    title: Optional[str],
    company: Optional[str],
    location: Optional[str],
    source: Optional[str],
    job_url: Optional[str],
    description: str,
) -> dict:
    cleaned_description = clean_text(description) or ""

    normalized_title = clean_text(title) or infer_title_from_description(description) or "Unknown Title"
    normalized_company = clean_text(company) or infer_company_from_description(description) or "Unknown Company"

    return {
        "title": normalized_title,
        "company": normalized_company,
        "location": clean_text(location),
        "source": clean_text(source),
        "job_url": clean_text(job_url),
        "description": cleaned_description,
    }