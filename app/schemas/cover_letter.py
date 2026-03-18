from pydantic import BaseModel
from typing import List


class CoverLetterResponse(BaseModel):
    job_id: int
    profile_id: int
    target_job_title: str
    target_company: str

    opening_paragraph: str
    motivation_paragraph: str
    fit_paragraph: str
    closing_paragraph: str

    full_cover_letter: str
    improvement_notes: List[str]