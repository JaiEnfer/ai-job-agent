from pydantic import BaseModel
from typing import List, Optional


class LLMParsedJobResponse(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    seniority: Optional[str] = None
    years_of_experience: Optional[str] = None
    employment_type: Optional[str] = None
    work_model: Optional[str] = None
    german_required: bool = False
    english_required: bool = False
    visa_sponsorship_mentioned: bool = False
    keywords: List[str] = []
    summary: str