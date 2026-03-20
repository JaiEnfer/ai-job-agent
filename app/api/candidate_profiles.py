from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileParseResponse,
    CandidateProfileUpdate,
    CandidateProfileResponse,
)
from app.services.candidate_profile_parser import extract_profile_skills
from app.services.resume_parser import (
    extract_email,
    extract_links_from_resume,
    extract_location,
    extract_name,
    extract_phone,
    extract_profile_links,
    extract_text_from_resume,
    extract_urls,
    fetch_url_metadata,
    parse_resume_sections,
)

# Keep most fields short to avoid database errors when parsing noisy resumes.
MAX_FIELD_LENGTHS = {
    "full_name": 255,
    "email": 255,
    "phone": 100,
    "location": 255,
    "linkedin_url": 500,
    "github_url": 500,
    "portfolio_url": 500,
    "headline": 500,
    "work_authorization": 255,
    "visa_status": 255,
}


def _truncate_field(value: str | None, max_length: int) -> str | None:
    if value is None:
        return None
    return value.strip()[:max_length]


def _truncate_profile_data(profile_data: dict) -> dict:
    for field, max_len in MAX_FIELD_LENGTHS.items():
        if field in profile_data and profile_data[field] is not None:
            profile_data[field] = _truncate_field(profile_data[field], max_len)
    return profile_data


def _build_profile_data(text: str, extra_links: list, filename: str = "resume") -> dict:
    """Shared logic for extracting profile data from resume text.

    Used by both /upload and /parse endpoints to avoid duplication.
    """
    full_name = extract_name(text) or filename.split(".")[0]

    # Try to grab contact info from both parsed text and any mailto/tel links.
    email = extract_email(text)
    phone = extract_phone(text)

    profile_links = extract_profile_links(text, extra_urls=extra_links)
    email = email or profile_links.get("email")
    phone = phone or profile_links.get("phone")

    location = extract_location(text) or profile_links.get("location")

    sections = parse_resume_sections(text)

    # Only use joined skills if the list is non-empty, otherwise store None.
    extracted_skills = extract_profile_skills(text)
    skills = sections.get("skills") or (", ".join(extracted_skills) if extracted_skills else None)

    # Fetch metadata from the first few URLs (if any) to help fill missing fields.
    metadata: dict[str, str] = {}
    for url in extract_urls(text)[:3]:
        metadata = fetch_url_metadata(url)
        if metadata:
            break

    # Only fall back to raw text for summary if it contains meaningful content.
    summary_fallback = text[:5000] if len(text.strip()) > 100 else None

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin_url": profile_links.get("linkedin_url"),
        "github_url": profile_links.get("github_url"),
        "portfolio_url": profile_links.get("portfolio_url"),
        "headline": metadata.get("title"),
        "summary": sections.get("summary") or metadata.get("description") or summary_fallback,
        "skills": skills,
        "experience": sections.get("experience"),
        "education": sections.get("education"),
        "projects": sections.get("projects"),
        "certifications": sections.get("certifications"),
        "languages": sections.get("languages"),
    }


router = APIRouter(prefix="/candidate-profiles", tags=["candidate-profiles"])


@router.post("", response_model=CandidateProfileResponse)
def create_candidate_profile(
    profile: CandidateProfileCreate,
    db: Session = Depends(get_db)
):
    data = _truncate_profile_data(profile.model_dump())
    db_profile = CandidateProfile(**data)
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
    extra_links = extract_links_from_resume(cv)

    profile_data = _build_profile_data(text, extra_links, filename=cv.filename or "resume")
    profile_data = _truncate_profile_data(profile_data)

    db_profile = CandidateProfile(**{k: v for k, v in profile_data.items() if v is not None})
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.post("/parse", response_model=CandidateProfileParseResponse)
async def parse_candidate_profile(cv: UploadFile = File(...)):
    """Parse the uploaded CV and return extracted fields without persisting."""
    text = extract_text_from_resume(cv)
    extra_links = extract_links_from_resume(cv)

    profile_data = _build_profile_data(text, extra_links, filename=cv.filename or "resume")

    return {
        **profile_data,
        "raw_text": text,
        "extracted_links": extra_links,
    }


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