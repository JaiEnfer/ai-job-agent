from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse,
)
from app.services.candidate_profile_parser import extract_profile_skills
from app.services.resume_parser import (
    extract_email,
    extract_name,
    extract_phone,
    extract_profile_links,
    extract_text_from_resume,
    extract_urls,
    fetch_url_metadata,
    parse_resume_sections,
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


@router.post("/upload", response_model=CandidateProfileResponse)
async def upload_candidate_profile(
    cv: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    text = extract_text_from_resume(cv)

    full_name = extract_name(text) or cv.filename.split(".")[0]
    email = extract_email(text)
    phone = extract_phone(text)

    sections = parse_resume_sections(text)
    skills = sections.get("skills") or ", ".join(extract_profile_skills(text))

    profile_links = extract_profile_links(text)

    # Fetch simple metadata from the first found URL to help fill missing fields
    metadata: dict[str, str] = {}
    for url in extract_urls(text)[:3]:
        metadata = fetch_url_metadata(url)
        if metadata:
            break

    profile_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "linkedin_url": profile_links.get("linkedin_url"),
        "github_url": profile_links.get("github_url"),
        "portfolio_url": profile_links.get("portfolio_url"),
        "headline": metadata.get("title"),
        "summary": sections.get("summary") or metadata.get("description") or text[:5000],
        "skills": skills,
        "experience": sections.get("experience"),
        "education": sections.get("education"),
        "projects": sections.get("projects"),
        "certifications": sections.get("certifications"),
        "languages": sections.get("languages"),
    }

    db_profile = CandidateProfile(**{k: v for k, v in profile_data.items() if v is not None})
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