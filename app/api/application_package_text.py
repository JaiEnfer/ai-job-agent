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
)
from app.services.cover_letter_generator import (
    build_opening_paragraph,
    build_motivation_paragraph,
    build_fit_paragraph,
    build_closing_paragraph,
    build_full_cover_letter,
)
from app.services.ats_scorer import (
    build_profile_document_text,
    calculate_keyword_match,
    calculate_ats_readiness_score,
    get_ats_rating,
)

router = APIRouter(prefix="/application-package-text", tags=["application-package-text"])


@router.get("/{job_id}/{profile_id}")
def generate_application_package_text(job_id: int, profile_id: int, db: Session = Depends(get_db)):
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

    matched_skills, missing_skills, skill_match_score = calculate_skill_match(
        parsed_job["skills"],
        extracted_profile_skills,
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

    overall_score = calculate_overall_score(
        skill_match_score=skill_match_score,
        location_match=location_match,
        work_model_match=work_model_match,
        language_match=language_match,
        visa_match=visa_match,
    )
    recommendation = generate_recommendation(overall_score)

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
    _, missing_keywords, keyword_match_score = calculate_keyword_match(
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

    package_text = f"""
APPLICATION PACKAGE
===================

Target Role: {job.title}
Target Company: {job.company}
Job Location: {job.location or 'N/A'}

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
Language Match: {"Yes" if language_match else "No"}
Location Match: {"Yes" if location_match else "No"}
Visa Match: {"Yes" if visa_match else "No"}

ATS SUMMARY
-----------
ATS Readiness Score: {ats_readiness_score}
ATS Rating: {ats_rating}
Missing ATS Keywords: {", ".join(missing_keywords) if missing_keywords else "None"}

TAILORED CV SUMMARY
-------------------
{tailored_summary}

PRIORITIZED SKILLS
------------------
- """ + "\n- ".join(prioritized_skills) + """

EXPERIENCE HIGHLIGHTS
---------------------
- """ + "\n- ".join(tailored_experience_bullets) + """

PRIORITIZED PROJECTS
--------------------
- """ + "\n- ".join(prioritized_projects) + """

COVER LETTER
------------
""" + full_cover_letter

    return {"application_package_text": package_text.strip()}