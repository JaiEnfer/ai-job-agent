from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.schemas.job_match import JobMatchResponse
from app.services.jd_parser import parse_job_description
from app.services.candidate_profile_parser import extract_profile_skills
from app.services.job_matcher import (
    calculate_skill_match,
    evaluate_location_match,
    evaluate_work_model_match,
    evaluate_language_match,
    evaluate_visa_match,
    calculate_overall_score,
    generate_recommendation,
)

router = APIRouter(prefix="/job-match", tags=["job-match"])


@router.get("/{job_id}/{profile_id}", response_model=JobMatchResponse)
def match_job_to_profile(job_id: int, profile_id: int, db: Session = Depends(get_db)):
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

    matched_skills, missing_skills, skill_match_score = calculate_skill_match(
        parsed_job["skills"],
        profile_skills,
    )

    location_match = evaluate_location_match(
        job.location,
        profile.preferred_locations,
    )

    work_model_match = evaluate_work_model_match(
        parsed_job["work_model"],
        profile.open_to_remote,
    )

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

    overall_score = calculate_overall_score(
        skill_match_score=skill_match_score,
        location_match=location_match,
        work_model_match=work_model_match,
        language_match=language_match,
        visa_match=visa_match,
    )

    recommendation = generate_recommendation(overall_score)

    explanation = []

    explanation.append(
        f"Matched {len(matched_skills)} of {len(parsed_job['skills'])} extracted job skills."
    )

    if missing_skills:
        explanation.append(
            f"Missing important skills: {', '.join(missing_skills)}."
        )

    if location_match:
        explanation.append("Job location matches candidate preferences.")
    else:
        explanation.append("Job location does not clearly match candidate preferences.")

    if work_model_match is True:
        explanation.append("Work model is compatible with candidate preferences.")
    elif work_model_match is False:
        explanation.append("Work model may not fit candidate remote preferences.")
    else:
        explanation.append("Work model was not clearly specified in the job description.")

    if language_match:
        explanation.append("Language requirements appear satisfied.")
    else:
        explanation.append("Language requirements may not be fully satisfied.")

    if visa_match:
        explanation.append("Visa or work authorization situation appears compatible.")
    else:
        explanation.append("Visa sponsorship may be a blocker for this role.")

    return {
        "job_id": job.id,
        "profile_id": profile.id,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_score": skill_match_score,
        "location_match": location_match,
        "work_model_match": work_model_match,
        "language_match": language_match,
        "visa_match": visa_match,
        "overall_score": overall_score,
        "recommendation": recommendation,
        "explanation": explanation,
    }