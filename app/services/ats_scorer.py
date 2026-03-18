from typing import List


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def build_profile_document_text(
    headline: str,
    summary: str,
    skills: str,
    experience: str,
    projects: str,
    education: str,
    languages: str,
) -> str:
    return " ".join(
        [
            headline or "",
            summary or "",
            skills or "",
            experience or "",
            projects or "",
            education or "",
            languages or "",
        ]
    ).lower()


def calculate_keyword_match(
    extracted_job_keywords: List[str],
    profile_document_text: str,
) -> tuple[List[str], List[str], float]:
    if not extracted_job_keywords:
        return [], [], 0.0

    matched = []
    missing = []

    profile_text = normalize_text(profile_document_text)

    for keyword in extracted_job_keywords:
        if normalize_text(keyword) in profile_text:
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = (len(matched) / len(extracted_job_keywords)) * 100
    return matched, missing, round(score, 2)


def calculate_ats_readiness_score(
    keyword_match_score: float,
    language_match: bool,
    location_match: bool,
    visa_match: bool,
) -> float:
    score = 0.0
    score += keyword_match_score * 0.7
    score += (100 if language_match else 0) * 0.15
    score += (100 if location_match else 0) * 0.10
    score += (100 if visa_match else 0) * 0.05
    return round(score, 2)


def get_ats_rating(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "strong"
    if score >= 55:
        return "moderate"
    if score >= 40:
        return "weak"
    return "poor"


def build_ats_suggestions(
    missing_keywords: List[str],
    language_match: bool,
    location_match: bool,
    visa_match: bool,
) -> List[str]:
    suggestions = []

    if missing_keywords:
        suggestions.append(
            f"Add truthful evidence for these missing ATS keywords where relevant: {', '.join(missing_keywords[:8])}."
        )

    if not language_match:
        suggestions.append(
            "Reflect required language capability more clearly in the CV and cover letter."
        )

    if not location_match:
        suggestions.append(
            "Mention Germany location preference, relocation readiness, or local availability more clearly."
        )

    if not visa_match:
        suggestions.append(
            "Address work authorization or visa sponsorship requirements clearly and professionally."
        )

    if not suggestions:
        suggestions.append(
            "ATS alignment looks strong. Focus on clarity, role relevance, and concise formatting."
        )

    return suggestions