from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.services.jd_parser import parse_job_description
from app.services.candidate_profile_parser import extract_profile_skills
from app.services.job_matcher import (
    calculate_skill_match,
    evaluate_location_match,
    evaluate_language_match,
    evaluate_visa_match,
)
from app.services.cover_letter_generator import (
    build_opening_paragraph,
    build_motivation_paragraph,
    build_fit_paragraph,
    build_closing_paragraph,
    build_full_cover_letter,
)

router = APIRouter(prefix="/cover-letter-text", tags=["cover-letter-text"])


@router.get("/{job_id}/{profile_id}")
def generate_cover_letter_text(job_id: int, profile_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    parsed_job = parse_job_description(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
    )

    profile_skills = extract_profile_skills(
        profile.headline or "",
        profile.summary or "",
        profile.skills or "",
        profile.experience or "",
        profile.projects or "",
    )

    matched_skills, missing_skills, _ = calculate_skill_match(
        parsed_job["skills"],
        profile_skills,
    )

    _location_match = evaluate_location_match(
        job.location,
        profile.preferred_locations,
    )

    _language_match = evaluate_language_match(
        parsed_job["german_required"],
        parsed_job["english_required"],
        profile.languages,
    )

    _visa_match = evaluate_visa_match(
        parsed_job["visa_sponsorship_mentioned"],
        profile.work_authorization,
        profile.visa_status,
    )

    opening_paragraph = build_opening_paragraph(
        full_name=profile.full_name,
        target_job_title=job.title,
        target_company=job.company,
    )

    motivation_paragraph = build_motivation_paragraph(
        target_job_title=job.title,
        target_company=job.company,
        summary=profile.summary or "",
        preferred_locations=profile.preferred_locations or "",
    )

    fit_paragraph = build_fit_paragraph(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        experience=profile.experience or "",
        projects=profile.projects or "",
    )

    closing_paragraph = build_closing_paragraph(
        target_company=job.company,
        visa_status=profile.visa_status or "",
        work_authorization=profile.work_authorization or "",
    )

    full_cover_letter = build_full_cover_letter(
        full_name=profile.full_name,
        opening_paragraph=opening_paragraph,
        motivation_paragraph=motivation_paragraph,
        fit_paragraph=fit_paragraph,
        closing_paragraph=closing_paragraph,
    )

    return {"cover_letter_text": full_cover_letter}