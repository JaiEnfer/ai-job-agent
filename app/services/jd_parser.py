import re
from typing import List, Optional


COMMON_SKILLS = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "nlp",
    "llm",
    "rag",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "fastapi",
    "django",
    "flask",
    "postgresql",
    "mysql",
    "git",
    "linux",
    "airflow",
    "mlops",
    "data science",
    "statistics",
    "computer vision",
    "langchain",
]


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found_skills = []

    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def extract_seniority(text: str) -> Optional[str]:
    text_lower = text.lower()

    if any(word in text_lower for word in ["senior", "sr."]):
        return "senior"
    if any(word in text_lower for word in ["staff", "principal", "lead"]):
        return "lead"
    if any(word in text_lower for word in ["mid-level", "mid level", "intermediate"]):
        return "mid"
    if any(word in text_lower for word in ["junior", "jr.", "entry level", "entry-level"]):
        return "junior"
    if any(word in text_lower for word in ["intern", "internship", "working student", "werkstudent"]):
        return "intern"

    return None


def extract_years_of_experience(text: str) -> Optional[str]:
    patterns = [
        r"(\d+\+?\s+years? of experience)",
        r"(\d+\+?\s+years? experience)",
        r"(\d+\+?\s+years? in)",
        r"(\d+\-\d+\s+years? of experience)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)

    return None


def extract_employment_type(text: str) -> Optional[str]:
    text_lower = text.lower()

    if "full-time" in text_lower or "full time" in text_lower or "vollzeit" in text_lower:
        return "full-time"
    if "part-time" in text_lower or "part time" in text_lower or "teilzeit" in text_lower:
        return "part-time"
    if "contract" in text_lower or "befristet" in text_lower:
        return "contract"
    if "internship" in text_lower or "praktikum" in text_lower or "werkstudent" in text_lower:
        return "internship"

    return None


def extract_work_model(text: str) -> Optional[str]:
    text_lower = text.lower()

    if "hybrid" in text_lower:
        return "hybrid"
    if "remote" in text_lower:
        return "remote"
    if "on-site" in text_lower or "onsite" in text_lower or "on site" in text_lower:
        return "onsite"

    return None


def extract_language_requirements(text: str) -> tuple[bool, bool]:
    text_lower = text.lower()

    german_phrases = [
        "german required",
        "fluent german",
        "german language",
        "good german",
        "business fluent german",
        "deutsch",
        "sehr gute deutschkenntnisse",
        "deutschkenntnisse",
        "verhandlungssicher deutsch",
        "c1 german",
        "b2 german",
        "german is a must",
        "must speak german",
    ]

    english_phrases = [
        "english required",
        "fluent english",
        "english language",
        "good english",
        "business fluent english",
        "c1 english",
        "b2 english",
        "english is required",
        "must speak english",
    ]

    german_required = any(phrase in text_lower for phrase in german_phrases)
    english_required = any(phrase in text_lower for phrase in english_phrases)

    return german_required, english_required


def extract_visa_sponsorship(text: str) -> bool:
    text_lower = text.lower()

    phrases = [
        "visa sponsorship",
        "sponsorship available",
        "work permit",
        "blue card",
        "eu blue card",
        "relocation support",
    ]

    return any(phrase in text_lower for phrase in phrases)


def extract_keywords(text: str) -> List[str]:
    text_lower = text.lower()

    keyword_candidates = [
        "python",
        "sql",
        "docker",
        "aws",
        "azure",
        "gcp",
        "machine learning",
        "deep learning",
        "nlp",
        "llm",
        "rag",
        "fastapi",
        "api",
        "microservices",
        "data pipelines",
        "etl",
        "mlops",
        "ci/cd",
        "statistics",
        "experimentation",
        "a/b testing",
    ]

    found = [keyword for keyword in keyword_candidates if keyword in text_lower]
    return sorted(list(set(found)))


def parse_job_description(
    title: Optional[str],
    company: Optional[str],
    location: Optional[str],
    description: str,
) -> dict:
    german_required, english_required = extract_language_requirements(description)

    return {
        "title": title,
        "company": company,
        "location": location,
        "skills": extract_skills(description),
        "seniority": extract_seniority(description),
        "years_of_experience": extract_years_of_experience(description),
        "employment_type": extract_employment_type(description),
        "work_model": extract_work_model(description),
        "german_required": german_required,
        "english_required": english_required,
        "visa_sponsorship_mentioned": extract_visa_sponsorship(description),
        "keywords": extract_keywords(description),
    }