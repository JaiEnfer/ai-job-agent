from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.session import get_db
from app.models.candidate_profile import CandidateProfile
from app.services.candidate_profile_parser import extract_profile_skills

router = APIRouter(prefix="/candidate-profile-analysis", tags=["candidate-profile-analysis"])


class CandidateProfileAnalysisResponse(BaseModel):
    profile_id: int
    full_name: str
    extracted_skills: List[str]
    target_roles: str | None = None
    preferred_locations: str | None = None
    work_authorization: str | None = None
    visa_status: str | None = None
    open_to_relocation: bool
    open_to_remote: bool


@router.get("/{profile_id}", response_model=CandidateProfileAnalysisResponse)
def analyze_candidate_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    extracted_skills = extract_profile_skills(
        profile.headline or "",
        profile.summary or "",
        profile.skills or "",
        profile.experience or "",
        profile.projects or "",
    )

    return {
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "extracted_skills": extracted_skills,
        "target_roles": profile.target_roles,
        "preferred_locations": profile.preferred_locations,
        "work_authorization": profile.work_authorization,
        "visa_status": profile.visa_status,
        "open_to_relocation": profile.open_to_relocation,
        "open_to_remote": profile.open_to_remote,
    }