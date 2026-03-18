from pydantic import BaseModel
from datetime import datetime


class ApplicationPackageRecordResponse(BaseModel):
    id: int
    job_id: int
    profile_id: int

    parsed_job_json: str
    candidate_profile_analysis_json: str
    match_result_json: str
    tailored_cv_json: str
    cover_letter_json: str
    ats_score_json: str

    application_package_text: str
    status: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True