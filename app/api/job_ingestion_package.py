import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.models.application_package import ApplicationPackage
from app.schemas.application_package_record import ApplicationPackageRecordResponse
from app.schemas.job_ingestion import RawJobIngestionRequest
from app.services.job_ingestion import normalize_job_payload
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
from app.services.cv_generator import (
    build_tailored_summary,
    build_prioritized_skills,
    build_tailored_experience_bullets,
    build_prioritized_projects,
    build_improvement_suggestions,
)
from app.services.cover_letter_generator import (
    build_opening_paragraph,
    build_motivation_paragraph,
    build_fit_paragraph,
    build_closing_paragraph,
    build_improvement_notes,
    build_full_cover_letter,
)
from app.services.ats_scorer import (
    build_profile_document_text,
    calculate_keyword_match,
    calculate_ats_readiness_score,
    get_ats_rating,
    build_ats_suggestions,
)

router = APIRouter(prefix="/job-ingestion-package", tags=["job-ingestion-package"])


@router.post("/generate/{profile_id}", response_model=ApplicationPackageRecordResponse)
def ingest_job_and_generate_package(
    profile_id: int,
    payload: RawJobIngestionRequest,
    db: Session = Depends(get_db),
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    normalized = normalize_job_payload(
        title=payload.title,
        company=payload.company,
        location=payload.location,
        source=payload.source,
        job_url=payload.job_url,
        description=payload.description,
    )

    if normalized["job_url"]:
        existing_job = db.query(Job).filter(Job.job_url == normalized["job_url"]).first()
        if existing_job:
            raise HTTPException(status_code=400, detail="Job with this URL already exists")

    db_job = Job(**normalized)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    parsed_job = parse_job_description(
        title=db_job.title,
        company=db_job.company,
        location=db_job.location,
        description=db_job.description,
    )

    extracted_profile_skills = extract_profile_skills(
        profile.headline or "",
        profile.summary or "",
        profile.skills or "",
        profile.experience or "",
        profile.projects or "",
    )

    candidate_profile_analysis = {
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "extracted_skills": extracted_profile_skills,
        "target_roles": profile.target_roles,
        "preferred_locations": profile.preferred_locations,
        "work_authorization": profile.work_authorization,
        "visa_status": profile.visa_status,
        "open_to_relocation": profile.open_to_relocation,
        "open_to_remote": profile.open_to_remote,
    }

    matched_skills, missing_skills, skill_match_score = calculate_skill_match(
        parsed_job["skills"],
        extracted_profile_skills,
    )

    location_match = evaluate_location_match(db_job.location, profile.preferred_locations)
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

    overall_score = calculate_overall_score(
        skill_match_score=skill_match_score,
        location_match=location_match,
        work_model_match=work_model_match,
        language_match=language_match,
        visa_match=visa_match,
    )

    recommendation = generate_recommendation(overall_score)

    match_result = {
        "job_id": db_job.id,
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
        "explanation": [
            f"Matched {len(matched_skills)} of {len(parsed_job['skills'])} extracted job skills."
        ],
    }

    tailored_summary = build_tailored_summary(
        full_name=profile.full_name,
        headline=profile.headline or "",
        summary=profile.summary or "",
        matched_skills=matched_skills,
        target_job_title=db_job.title,
        target_company=db_job.company,
    )

    prioritized_skills = build_prioritized_skills(
        matched_skills=matched_skills,
        profile_skills=extracted_profile_skills,
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

    tailored_cv = {
        "job_id": db_job.id,
        "profile_id": profile.id,
        "target_job_title": db_job.title,
        "target_company": db_job.company,
        "tailored_summary": tailored_summary,
        "prioritized_skills": prioritized_skills,
        "tailored_experience_bullets": tailored_experience_bullets,
        "prioritized_projects": prioritized_projects,
        "improvement_suggestions": build_improvement_suggestions(
            missing_skills=missing_skills,
            language_match=language_match,
            visa_match=visa_match,
            location_match=location_match,
        ),
    }

    opening_paragraph = build_opening_paragraph(
        full_name=profile.full_name,
        target_job_title=db_job.title,
        target_company=db_job.company,
    )

    motivation_paragraph = build_motivation_paragraph(
        target_job_title=db_job.title,
        target_company=db_job.company,
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
        target_company=db_job.company,
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

    cover_letter = {
        "job_id": db_job.id,
        "profile_id": profile.id,
        "target_job_title": db_job.title,
        "target_company": db_job.company,
        "opening_paragraph": opening_paragraph,
        "motivation_paragraph": motivation_paragraph,
        "fit_paragraph": fit_paragraph,
        "closing_paragraph": closing_paragraph,
        "full_cover_letter": full_cover_letter,
        "improvement_notes": build_improvement_notes(
            missing_skills=missing_skills,
            language_match=language_match,
            visa_match=visa_match,
            location_match=location_match,
        ),
    }

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

    matched_keywords, missing_keywords_ats, keyword_match_score = calculate_keyword_match(
        extracted_job_keywords=combined_keywords,
        profile_document_text=profile_document_text,
    )

    ats_readiness_score = calculate_ats_readiness_score(
        keyword_match_score=keyword_match_score,
        language_match=language_match,
        location_match=location_match,
        visa_match=visa_match,
    )

    ats_score = {
        "job_id": db_job.id,
        "profile_id": profile.id,
        "extracted_job_keywords": combined_keywords,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords_ats,
        "keyword_match_score": keyword_match_score,
        "language_match": language_match,
        "location_match": location_match,
        "visa_match": visa_match,
        "ats_readiness_score": ats_readiness_score,
        "ats_rating": get_ats_rating(ats_readiness_score),
        "suggestions": build_ats_suggestions(
            missing_keywords=missing_keywords_ats,
            language_match=language_match,
            location_match=location_match,
            visa_match=visa_match,
        ),
    }

    application_package_text = f"""
APPLICATION PACKAGE
===================

Target Role: {db_job.title}
Target Company: {db_job.company}
Job Location: {db_job.location or 'N/A'}

CANDIDATE
---------
Name: {profile.full_name}
Email: {profile.email or 'N/A'}
Phone: {profile.phone or 'N/A'}
Location: {profile.location or 'N/A'}

MATCH SUMMARY
-------------
Overall Match Score: {overall_score}
Recommendation: {recommendation}
Matched Skills: {", ".join(matched_skills) if matched_skills else "None"}
Missing Skills: {", ".join(missing_skills) if missing_skills else "None"}

ATS SUMMARY
-----------
ATS Readiness Score: {ats_readiness_score}
Missing ATS Keywords: {", ".join(missing_keywords_ats) if missing_keywords_ats else "None"}

TAILORED CV SUMMARY
-------------------
{tailored_summary}

COVER LETTER
------------
{full_cover_letter}
""".strip()

    db_record = ApplicationPackage(
        job_id=db_job.id,
        profile_id=profile.id,
        parsed_job_json=json.dumps(parsed_job),
        candidate_profile_analysis_json=json.dumps(candidate_profile_analysis),
        match_result_json=json.dumps(match_result),
        tailored_cv_json=json.dumps(tailored_cv),
        cover_letter_json=json.dumps(cover_letter),
        ats_score_json=json.dumps(ats_score),
        application_package_text=application_package_text,
        status="generated",
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record