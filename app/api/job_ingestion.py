from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.job_ingestion import (
    RawJobIngestionRequest,
    StructuredJobIngestionRequest,
    JobIngestionResponse,
)
from app.services.job_ingestion import normalize_job_payload
from app.services.jd_parser import parse_job_description

router = APIRouter(prefix="/job-ingestion", tags=["job-ingestion"])


@router.post("/raw", response_model=JobIngestionResponse)
def ingest_raw_job(payload: RawJobIngestionRequest, db: Session = Depends(get_db)):
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

    return {
        "stored_job": db_job,
        "parsed_job": parsed_job,
    }


@router.post("/structured", response_model=JobIngestionResponse)
def ingest_structured_job(payload: StructuredJobIngestionRequest, db: Session = Depends(get_db)):
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

    return {
        "stored_job": db_job,
        "parsed_job": parsed_job,
    }