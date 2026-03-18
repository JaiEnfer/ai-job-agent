from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse,
)

router = APIRouter(prefix="/candidate-profiles", tags=["candidate-profiles"])


@router.post("", response_model=CandidateProfileResponse)
def create_candidate_profile(
    profile: CandidateProfileCreate,
    db: Session = Depends(get_db)
):
    db_profile = CandidateProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("", response_model=list[CandidateProfileResponse])
def list_candidate_profiles(db: Session = Depends(get_db)):
    profiles = db.query(CandidateProfile).order_by(CandidateProfile.created_at.desc()).all()
    return profiles


@router.get("/{profile_id}", response_model=CandidateProfileResponse)
def get_candidate_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    return profile


@router.put("/{profile_id}", response_model=CandidateProfileResponse)
def update_candidate_profile(
    profile_id: int,
    updated_profile: CandidateProfileUpdate,
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    for field, value in updated_profile.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}")
def delete_candidate_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    db.delete(profile)
    db.commit()
    return {"message": f"Candidate profile {profile_id} deleted successfully"}