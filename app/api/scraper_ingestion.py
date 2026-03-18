from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.scraper_ingestion import ScrapeAndIngestRequest, ScrapeAndIngestResponse
from app.services.scrapers.site_extractors import extract_job_text_from_site
from app.services.job_ingestion import normalize_job_payload
from app.services.jd_parser import parse_job_description

router = APIRouter(prefix="/scraper-ingestion", tags=["scraper-ingestion"])


@router.post("/job-url", response_model=ScrapeAndIngestResponse)
def scrape_and_ingest_job(payload: ScrapeAndIngestRequest, db: Session = Depends(get_db)):
    existing_job = db.query(Job).filter(Job.job_url == str(payload.url)).first()
    if existing_job:
        raise HTTPException(status_code=400, detail="Job with this URL already exists")

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

    parsed_job = parse_job_description(
        title=db_job.title,
        company=db_job.company,
        location=db_job.location,
        description=db_job.description,
    )

    return {
        "stored_job": db_job,
        "parsed_job": parsed_job,
        "scraped_page_title": scraped["page_title"],
        "scraped_source_url": scraped["source_url"],
    }