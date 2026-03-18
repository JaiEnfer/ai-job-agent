from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.schemas.ats_score import ATSScoreResponse
from app.services.jd_parser import parse_job_description
from app.services.job_matcher import (
    evaluate_location_match,
    evaluate_language_match,
    evaluate_visa_match,
)
from app.services.ats_scorer import (
    build_profile_document_text,
    calculate_keyword_match,
    calculate_ats_readiness_score,
    get_ats_rating,
    build_ats_suggestions,
)

router = APIRouter(prefix="/ats-score", tags=["ats-score"])


@router.get("/{job_id}/{profile_id}", response_model=ATSScoreResponse)
def score_ats_fit(job_id: int, profile_id: int, db: Session = Depends(get_db)):
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

    combined_keywords = sorted(list(set(parsed_job["keywords"] + parsed_job["skills"])))

    profile_document_text = build_profile_document_text(
        headline=profile.headline or "",
        summary=profile.summary or "",
        skills=profile.skills or "",
        experience=profile.experience or "",
        projects=profile.projects or "",
        education=profile.education or "",
        languages=profile.languages or "",
    )

    matched_keywords, missing_keywords, keyword_match_score = calculate_keyword_match(
        extracted_job_keywords=combined_keywords,
        profile_document_text=profile_document_text,
    )

    language_match = evaluate_language_match(
        parsed_job["german_required"],
        parsed_job["english_required"],
        profile.languages,
    )

    location_match = evaluate_location_match(
        job.location,
        profile.preferred_locations,
    )

    visa_match = evaluate_visa_match(
        parsed_job["visa_sponsorship_mentioned"],
        profile.work_authorization,
        profile.visa_status,
    )

    ats_readiness_score = calculate_ats_readiness_score(
        keyword_match_score=keyword_match_score,
        language_match=language_match,
        location_match=location_match,
        visa_match=visa_match,
    )

    ats_rating = get_ats_rating(ats_readiness_score)

    suggestions = build_ats_suggestions(
        missing_keywords=missing_keywords,
        language_match=language_match,
        location_match=location_match,
        visa_match=visa_match,
    )

    return {
        "job_id": job.id,
        "profile_id": profile.id,
        "extracted_job_keywords": combined_keywords,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "keyword_match_score": keyword_match_score,
        "language_match": language_match,
        "location_match": location_match,
        "visa_match": visa_match,
        "ats_readiness_score": ats_readiness_score,
        "ats_rating": ats_rating,
        "suggestions": suggestions,
    }