from pydantic import BaseModel
from typing import List, Optional

from app.schemas.job_parser import ParsedJobResponse
from app.schemas.job_match import JobMatchResponse
from app.schemas.cv_generator import TailoredCVResponse
from app.schemas.cover_letter import CoverLetterResponse
from app.schemas.ats_score import ATSScoreResponse


class CandidateProfileAnalysisPackage(BaseModel):
    profile_id: int
    full_name: str
    extracted_skills: List[str]
    target_roles: Optional[str] = None
    preferred_locations: Optional[str] = None
    work_authorization: Optional[str] = None
    visa_status: Optional[str] = None
    open_to_relocation: bool
    open_to_remote: bool


class ApplicationPackageResponse(BaseModel):
    job_id: int
    profile_id: int

    parsed_job: ParsedJobResponse
    candidate_profile_analysis: CandidateProfileAnalysisPackage
    match_result: JobMatchResponse
    tailored_cv: TailoredCVResponse
    cover_letter: CoverLetterResponse
    ats_score: ATSScoreResponse