from pydantic import BaseModel
from typing import List


class ATSScoreResponse(BaseModel):
    job_id: int
    profile_id: int

    extracted_job_keywords: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]

    keyword_match_score: float
    language_match: bool
    location_match: bool
    visa_match: bool

    ats_readiness_score: float
    ats_rating: str
    suggestions: List[str]