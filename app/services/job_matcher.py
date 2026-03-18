from typing import List, Optional


def normalize_text_list(value: Optional[str]) -> List[str]:
    if not value:
        return []

    parts = [item.strip().lower() for item in value.split(",")]
    return [item for item in parts if item]


def calculate_skill_match(job_skills: List[str], profile_skills: List[str]) -> tuple[List[str], List[str], float]:
    job_skill_set = set(skill.lower() for skill in job_skills)
    profile_skill_set = set(skill.lower() for skill in profile_skills)

    matched = sorted(list(job_skill_set.intersection(profile_skill_set)))
    missing = sorted(list(job_skill_set.difference(profile_skill_set)))

    if not job_skill_set:
        return matched, missing, 0.0

    score = (len(matched) / len(job_skill_set)) * 100
    return matched, missing, round(score, 2)


def evaluate_location_match(job_location: Optional[str], preferred_locations: Optional[str]) -> bool:
    if not job_location:
        return False

    job_location_lower = job_location.lower()

    if "germany" in job_location_lower and preferred_locations:
        preferred_list = normalize_text_list(preferred_locations)
        germany_related = ["berlin", "munich", "hamburg", "frankfurt", "cologne", "remote germany", "germany"]

        if any(pref in job_location_lower for pref in preferred_list):
            return True

        if any(pref in germany_related for pref in preferred_list):
            return True

    if not preferred_locations:
        return False

    preferred_list = normalize_text_list(preferred_locations)
    return any(preferred in job_location_lower for preferred in preferred_list)


def evaluate_work_model_match(job_work_model: Optional[str], open_to_remote: bool) -> Optional[bool]:
    if not job_work_model:
        return None

    if job_work_model == "remote":
        return open_to_remote

    return True


def evaluate_language_match(
    german_required: bool,
    english_required: bool,
    profile_languages: Optional[str]
) -> bool:
    if not profile_languages:
        return not german_required and not english_required

    languages_text = profile_languages.lower()

    german_ok = True
    english_ok = True

    if german_required:
        german_ok = "german" in languages_text or "deutsch" in languages_text

    if english_required:
        english_ok = "english" in languages_text

    return german_ok and english_ok


def evaluate_visa_match(
    visa_sponsorship_mentioned: bool,
    work_authorization: Optional[str],
    visa_status: Optional[str]
) -> bool:
    combined = f"{work_authorization or ''} {visa_status or ''}".lower()

    if "visa" in combined or "sponsorship" in combined or "blue card" in combined:
        return visa_sponsorship_mentioned

    return True


def calculate_overall_score(
    skill_match_score: float,
    location_match: bool,
    work_model_match: Optional[bool],
    language_match: bool,
    visa_match: bool
) -> float:
    score = 0.0

    score += skill_match_score * 0.6
    score += (100 if location_match else 0) * 0.15
    score += (100 if language_match else 0) * 0.15
    score += (100 if visa_match else 0) * 0.05

    if work_model_match is None:
        score += 5
    else:
        score += (100 if work_model_match else 0) * 0.05

    return round(score, 2)


def generate_recommendation(overall_score: float) -> str:
    if overall_score >= 80:
        return "strong_apply"
    if overall_score >= 60:
        return "apply"
    if overall_score >= 40:
        return "consider"
    return "low_fit"