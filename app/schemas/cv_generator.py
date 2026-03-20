from pydantic import BaseModel
from typing import List


class TailoredCVResponse(BaseModel):
    job_id: int
    profile_id: int
    target_job_title: str
    target_company: str

    tailored_summary: str
    prioritized_skills: List[str]
    tailored_experience_bullets: List[str]
    prioritized_projects: List[str]
    improvement_suggestions: List[str]

    # Optional: LLM-generated rewritten CV (senior recruiter persona)
    rewritten_cv: str | None = None