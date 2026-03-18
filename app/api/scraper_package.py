from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.schemas.scraper_ingestion import ScrapeAndIngestRequest
from app.services.scrapers.site_extractors import extract_job_text_from_site
from app.services.job_ingestion import normalize_job_payload

router = APIRouter(prefix="/scraper-package", tags=["scraper-package"])


@router.post("/generate/{profile_id}")
def scrape_ingest_and_prepare_package(profile_id: int, payload: ScrapeAndIngestRequest, db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    existing_job = db.query(Job).filter(Job.job_url == str(payload.url)).first()
    if existing_job:
        return {
            "message": "Job URL already exists. Use the existing job to generate package.",
            "job_id": existing_job.id,
            "profile_id": profile_id,
        }

    scraped = extract_job_text_from_site(str(payload.url))

    normalized = normalize_job_payload(
        title=scraped["page_title"],
        company=payload.company,
        location=payload.location,
        source=payload.source or scraped["site_name"],
        job_url=str(payload.url),
        description=scraped["raw_text"],
    )

    db_job = Job(**normalized)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return {
        "message": "Job scraped and stored successfully. Next use /application-package or /job-ingestion-package flow.",
        "job_id": db_job.id,
        "profile_id": profile_id,
        "scraped_page_title": scraped["page_title"],
        "scraped_source_url": scraped["source_url"],
        "site_name": scraped["site_name"],
        "used_selector_strategy": scraped["used_selector_strategy"],
    }