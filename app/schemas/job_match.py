from pydantic import BaseModel
from typing import List, Optional


class JobMatchResponse(BaseModel):
    job_id: int
    profile_id: int

    matched_skills: List[str]
    missing_skills: List[str]

    skill_match_score: float
    location_match: bool
    work_model_match: Optional[bool] = None
    language_match: bool
    visa_match: bool

    overall_score: float
    recommendation: str
    explanation: List[str]