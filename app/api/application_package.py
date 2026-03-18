from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.schemas.application_package import ApplicationPackageResponse
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

router = APIRouter(prefix="/application-package", tags=["application-package"])


@router.get("/{job_id}/{profile_id}", response_model=ApplicationPackageResponse)
def generate_application_package(job_id: int, profile_id: int, db: Session = Depends(get_db)):
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

    match_explanation = []
    match_explanation.append(
        f"Matched {len(matched_skills)} of {len(parsed_job['skills'])} extracted job skills."
    )

    if missing_skills:
        match_explanation.append(
            f"Missing important skills: {', '.join(missing_skills)}."
        )

    if location_match:
        match_explanation.append("Job location matches candidate preferences.")
    else:
        match_explanation.append("Job location does not clearly match candidate preferences.")

    if work_model_match is True:
        match_explanation.append("Work model is compatible with candidate preferences.")
    elif work_model_match is False:
        match_explanation.append("Work model may not fit candidate remote preferences.")
    else:
        match_explanation.append("Work model was not clearly specified in the job description.")

    if language_match:
        match_explanation.append("Language requirements appear satisfied.")
    else:
        match_explanation.append("Language requirements may not be fully satisfied.")

    if visa_match:
        match_explanation.append("Visa or work authorization situation appears compatible.")
    else:
        match_explanation.append("Visa sponsorship may be a blocker for this role.")

    match_result = {
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
        "explanation": match_explanation,
    }

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

    cv_improvement_suggestions = build_improvement_suggestions(
        missing_skills=missing_skills,
        language_match=language_match,
        visa_match=visa_match,
        location_match=location_match,
    )

    tailored_cv = {
        "job_id": job.id,
        "profile_id": profile.id,
        "target_job_title": job.title,
        "target_company": job.company,
        "tailored_summary": tailored_summary,
        "prioritized_skills": prioritized_skills,
        "tailored_experience_bullets": tailored_experience_bullets,
        "prioritized_projects": prioritized_projects,
        "improvement_suggestions": cv_improvement_suggestions,
    }

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

    cover_letter_notes = build_improvement_notes(
        missing_skills=missing_skills,
        language_match=language_match,
        visa_match=visa_match,
        location_match=location_match,
    )

    full_cover_letter = build_full_cover_letter(
        full_name=profile.full_name,
        opening_paragraph=opening_paragraph,
        motivation_paragraph=motivation_paragraph,
        fit_paragraph=fit_paragraph,
        closing_paragraph=closing_paragraph,
    )

    cover_letter = {
        "job_id": job.id,
        "profile_id": profile.id,
        "target_job_title": job.title,
        "target_company": job.company,
        "opening_paragraph": opening_paragraph,
        "motivation_paragraph": motivation_paragraph,
        "fit_paragraph": fit_paragraph,
        "closing_paragraph": closing_paragraph,
        "full_cover_letter": full_cover_letter,
        "improvement_notes": cover_letter_notes,
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

    ats_rating = get_ats_rating(ats_readiness_score)

    ats_suggestions = build_ats_suggestions(
        missing_keywords=missing_keywords_ats,
        language_match=language_match,
        location_match=location_match,
        visa_match=visa_match,
    )

    ats_score = {
        "job_id": job.id,
        "profile_id": profile.id,
        "extracted_job_keywords": combined_keywords,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords_ats,
        "keyword_match_score": keyword_match_score,
        "language_match": language_match,
        "location_match": location_match,
        "visa_match": visa_match,
        "ats_readiness_score": ats_readiness_score,
        "ats_rating": ats_rating,
        "suggestions": ats_suggestions,
    }

    return {
        "job_id": job.id,
        "profile_id": profile.id,
        "parsed_job": parsed_job,
        "candidate_profile_analysis": candidate_profile_analysis,
        "match_result": match_result,
        "tailored_cv": tailored_cv,
        "cover_letter": cover_letter,
        "ats_score": ats_score,
    }