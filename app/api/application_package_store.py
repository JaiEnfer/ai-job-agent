import io
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.models.application_package import ApplicationPackage
from app.schemas.application_package_record import ApplicationPackageRecordResponse
from app.schemas.application_package_status import ApplicationPackageStatusUpdate
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
from app.services.llm_cv_rewriter import rewrite_cv_as_recruiter
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

router = APIRouter(prefix="/application-package-store", tags=["application-package-store"])


@router.post("/generate/{job_id}/{profile_id}", response_model=ApplicationPackageRecordResponse)
def save_application_package(
    job_id: int,
    profile_id: int,
    language: str = "english",
    db: Session = Depends(get_db),
):
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
        "work_authorization": profile.work_authorization,
        "visa_status": profile.visa_status,
        "open_to_relocation": profile.open_to_relocation,
        "open_to_remote": profile.open_to_remote,
    }

    matched_skills, missing_skills, skill_match_score = calculate_skill_match(
        parsed_job["skills"],
        extracted_profile_skills,
    )

    location_match = evaluate_location_match(job.location, profile.preferred_locations if hasattr(profile, 'preferred_locations') else None)
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

    match_explanation = [
        f"Matched {len(matched_skills)} of {len(parsed_job['skills'])} extracted job skills."
    ]

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
        language=language,
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
        "rewritten_cv": rewritten_cv,
    }

    opening_paragraph = build_opening_paragraph(
        full_name=profile.full_name,
        target_job_title=job.title,
        target_company=job.company,
        language=language,
    )

    motivation_paragraph = build_motivation_paragraph(
        target_job_title=job.title,
        target_company=job.company,
        summary=profile.summary or "",
        preferred_locations=getattr(profile, 'preferred_locations', None) or "",
        language=language,
    )

    fit_paragraph = build_fit_paragraph(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        experience=profile.experience or "",
        projects=profile.projects or "",
        language=language,
    )

    closing_paragraph = build_closing_paragraph(
        target_company=job.company,
        visa_status=profile.visa_status or "",
        work_authorization=profile.work_authorization or "",
        language=language,
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
        language=language,
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

    application_package_text = f"""
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
Missing ATS Keywords: {", ".join(missing_keywords_ats) if missing_keywords_ats else "None"}

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
""" + full_cover_letter + f"""

LLM-REWRITTEN CV
----------------
{rewritten_cv}
"""

    db_record = ApplicationPackage(
        job_id=job.id,
        profile_id=profile.id,
        parsed_job_json=json.dumps(parsed_job),
        candidate_profile_analysis_json=json.dumps(candidate_profile_analysis),
        match_result_json=json.dumps(match_result),
        tailored_cv_json=json.dumps(tailored_cv),
        cover_letter_json=json.dumps(cover_letter),
        ats_score_json=json.dumps(ats_score),
        application_package_text=application_package_text.strip(),
        status="generated",
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


def _build_cv_plaintext(cv_json: dict) -> str:
    """Build CV text for PDF — uses the LLM-rewritten CV as the primary content."""
    rewritten = cv_json.get("rewritten_cv", "").strip()
    if rewritten:
        return rewritten

    # Fallback to structured fields if LLM rewrite is missing
    parts = []
    parts.append(f"Target Role: {cv_json.get('target_job_title', '')}")
    parts.append(f"Target Company: {cv_json.get('target_company', '')}")
    parts.append("")
    parts.append("SUMMARY")
    parts.append(cv_json.get("tailored_summary", ""))

    skills = cv_json.get("prioritized_skills", [])
    if skills:
        parts.append("")
        parts.append("SKILLS")
        for skill in skills:
            parts.append(f"- {skill}")

    bullets = cv_json.get("tailored_experience_bullets", [])
    if bullets:
        parts.append("")
        parts.append("EXPERIENCE HIGHLIGHTS")
        for bullet in bullets:
            parts.append(f"- {bullet}")

    projects = cv_json.get("prioritized_projects", [])
    if projects:
        parts.append("")
        parts.append("PROJECTS")
        for proj in projects:
            parts.append(f"- {proj}")

    return "\n".join(parts).strip()


def _build_cover_letter_plaintext(cover_letter_json: dict) -> str:
    if cover_letter_json.get("full_cover_letter"):
        return cover_letter_json["full_cover_letter"].strip()

    parts = []
    parts.append(cover_letter_json.get("opening_paragraph", "").strip())
    parts.append("")
    parts.append(cover_letter_json.get("motivation_paragraph", "").strip())
    parts.append("")
    parts.append(cover_letter_json.get("fit_paragraph", "").strip())
    parts.append("")
    parts.append(cover_letter_json.get("closing_paragraph", "").strip())
    parts.append("")
    parts.append("---")
    parts.append("Notes")
    parts.append("-----")
    for note in cover_letter_json.get("improvement_notes", []):
        parts.append(f"- {note}")

    return "\n".join([p for p in parts if p]).strip()


def _build_pdf(title: str, content: str) -> bytes:
    """Convert plain text content into a clean A4 PDF using reportlab."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CVTitle",
        parent=styles["Heading1"],
        fontSize=15,
        spaceAfter=8,
        textColor="#1a1a2e",
        leading=20,
    )
    heading_style = ParagraphStyle(
        "CVHeading",
        parent=styles["Heading2"],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=4,
        textColor="#1a1a2e",
        leading=15,
    )
    body_style = ParagraphStyle(
        "CVBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        spaceAfter=4,
        wordWrap="LTR",
        alignment=TA_LEFT,
    )
    bullet_style = ParagraphStyle(
        "CVBullet",
        parent=body_style,
        leftIndent=14,
        spaceAfter=3,
        leading=14,
    )

    def esc(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story = []
    story.append(Paragraph(esc(title), title_style))
    story.append(Spacer(1, 3 * mm))

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 2 * mm))
            continue

        # Skip pure divider lines
        if set(stripped) <= set("-=*"):
            continue

        # Bullet point
        if stripped.startswith("- ") or stripped.startswith("• "):
            text = stripped[2:].strip()
            story.append(Paragraph(f"• {esc(text)}", bullet_style))

        # Section heading: all caps, or short line that looks like a header
        elif (
            stripped.isupper()
            or (len(stripped) < 50 and stripped.endswith(":") and stripped[0].isupper())
            or (len(stripped) < 40 and stripped[0].isupper() and "\n" not in stripped
                and not any(c in stripped for c in [".", ",", "(", ")"]))
        ):
            story.append(Paragraph(esc(stripped), heading_style))

        else:
            story.append(Paragraph(esc(stripped), body_style))

    doc.build(story)
    return buffer.getvalue()


@router.get("/records/{package_id}/download/cv")
def download_application_package_cv(package_id: int, db: Session = Depends(get_db)):
    record = db.query(ApplicationPackage).filter(ApplicationPackage.id == package_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application package not found")

    try:
        cv_json = json.loads(record.tailored_cv_json or "{}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse CV data")

    content = _build_cv_plaintext(cv_json)
    title = f"Tailored CV — {cv_json.get('target_job_title', '')} @ {cv_json.get('target_company', '')}"

    pdf_bytes = _build_pdf(title, content)
    filename = f"tailored_cv_{package_id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/records/{package_id}/download/cover-letter")
def download_application_package_cover_letter(package_id: int, db: Session = Depends(get_db)):
    record = db.query(ApplicationPackage).filter(ApplicationPackage.id == package_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application package not found")

    try:
        cover_letter_json = json.loads(record.cover_letter_json or "{}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse cover letter data")

    content = _build_cover_letter_plaintext(cover_letter_json)
    title = f"Cover Letter — {cover_letter_json.get('target_job_title', '')} @ {cover_letter_json.get('target_company', '')}"

    pdf_bytes = _build_pdf(title, content)
    filename = f"cover_letter_{package_id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/records", response_model=list[ApplicationPackageRecordResponse])
def list_application_packages(db: Session = Depends(get_db)):
    records = db.query(ApplicationPackage).order_by(ApplicationPackage.created_at.desc()).all()
    return records


@router.get("/records/{package_id}", response_model=ApplicationPackageRecordResponse)
def get_application_package(package_id: int, db: Session = Depends(get_db)):
    record = db.query(ApplicationPackage).filter(ApplicationPackage.id == package_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application package not found")
    return record


@router.delete("/records/{package_id}")
def delete_application_package(package_id: int, db: Session = Depends(get_db)):
    record = db.query(ApplicationPackage).filter(ApplicationPackage.id == package_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application package not found")

    # Delete any linked Application rows first to avoid FK constraint violations.
    # Import here to avoid circular imports.
    try:
        from app.models.application import Application
        db.query(Application).filter(Application.application_package_id == package_id).delete()
    except Exception:
        pass  # No Application model or no linked rows — safe to continue

    db.delete(record)
    db.commit()
    return {"message": f"Application package {package_id} deleted successfully"}


@router.put("/records/{package_id}/status", response_model=ApplicationPackageRecordResponse)
def update_application_package_status(
    package_id: int,
    payload: ApplicationPackageStatusUpdate,
    db: Session = Depends(get_db)
):
    record = db.query(ApplicationPackage).filter(ApplicationPackage.id == package_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application package not found")
    record.status = payload.status
    db.commit()
    db.refresh(record)
    return record