from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.services.jd_parser import parse_job_description
from app.services.candidate_profile_parser import extract_profile_skills
from app.services.job_matcher import calculate_skill_match
from app.services.cv_generator import (
    build_tailored_summary,
    build_prioritized_skills,
    build_tailored_experience_bullets,
    build_prioritized_projects,
)

router = APIRouter(prefix="/cv-text", tags=["cv-text"])


@router.get("/{job_id}/{profile_id}")
def generate_cv_text(job_id: int, profile_id: int, db: Session = Depends(get_db)):
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

    tailored_summary = build_tailored_summary(
        full_name=profile.full_name,
        headline=profile.headline or "",
        summary=profile.summary or "",
        matched_skills=matched_skills,
        target_job_title=job.title,
        target_company=job.company,
    )

    prioritized_skills = build_prioritized_skills(
        matched_skills=matched_skills,
        profile_skills=profile_skills,
        missing_skills=missing_skills,
    )

    tailored_experience_bullets = build_tailored_experience_bullets(
        experience_text=profile.experience or "",
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )

    prioritized_projects = build_prioritized_projects(
        projects_text=profile.projects or "",
        matched_skills=matched_skills,
    )

    cv_text = f"""
{profile.full_name}
{profile.email or ''}
{profile.phone or ''}
{profile.location or ''}

Headline:
{profile.headline or ''}

Tailored Professional Summary:
{tailored_summary}

Prioritized Skills:
- """ + "\n- ".join(prioritized_skills) + """

Experience Highlights:
- """ + "\n- ".join(tailored_experience_bullets) + """

Projects:
- """ + "\n- ".join(prioritized_projects) + """

Education:
{profile.education or ''}

Languages:
{profile.languages or ''}
""".strip()

    return {"cv_text": cv_text}