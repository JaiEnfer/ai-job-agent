from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.schemas.cv_generator import TailoredCVResponse
from app.services.jd_parser import parse_job_description
from app.services.candidate_profile_parser import extract_profile_skills
from app.services.job_matcher import (
    calculate_skill_match,
    evaluate_location_match,
    evaluate_work_model_match,
    evaluate_language_match,
    evaluate_visa_match,
)
from app.services.cv_generator import (
    build_tailored_summary,
    build_prioritized_skills,
    build_tailored_experience_bullets,
    build_prioritized_projects,
    build_improvement_suggestions,
)
from app.services.llm_cv_rewriter import rewrite_cv_as_recruiter

router = APIRouter(prefix="/cv-generator", tags=["cv-generator"])


@router.get("/{job_id}/{profile_id}", response_model=TailoredCVResponse)
def generate_tailored_cv(job_id: int, profile_id: int, prompt: str | None = None, db: Session = Depends(get_db)):
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

    location_match = evaluate_location_match(job.location, profile.preferred_locations)
    work_model_match = evaluate_work_model_match(parsed_job["work_model"], profile.open_to_remote)
    language_match = evaluate_language_match(
        parsed_job["german_required"],
        parsed_job["english_required"],
        profile.languages,
    )
    visa_match = evaluate_visa_match(
        parsed_job["visa_sponsorship_mentioned"],
        profile.work_authorization,
        profile.visa_status,
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

    improvement_suggestions = build_improvement_suggestions(
        missing_skills=missing_skills,
        language_match=language_match,
        visa_match=visa_match,
        location_match=location_match,
    )

    rewritten_cv = rewrite_cv_as_recruiter(
        job_title=job.title,
        job_company=job.company,
        job_location=job.location,
        job_description=job.description,
        full_name=profile.full_name,
        headline=profile.headline or "",
        summary=profile.summary or "",
        skills=profile.skills or "",
        experience=profile.experience or "",
        projects=profile.projects or "",
        prompt=prompt,
    )

    return {
        "job_id": job.id,
        "profile_id": profile.id,
        "target_job_title": job.title,
        "target_company": job.company,
        "tailored_summary": tailored_summary,
        "prioritized_skills": prioritized_skills,
        "tailored_experience_bullets": tailored_experience_bullets,
        "prioritized_projects": prioritized_projects,
        "improvement_suggestions": improvement_suggestions,
        "rewritten_cv": rewritten_cv,
    }