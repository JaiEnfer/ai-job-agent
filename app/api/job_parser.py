from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.job_parser import ParsedJobResponse
from app.services.jd_parser import parse_job_description

router = APIRouter(prefix="/job-parser", tags=["job-parser"])


class RawJobParseRequest(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str


@router.get("/{job_id}", response_model=ParsedJobResponse)
def parse_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    parsed = parse_job_description(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
    )

    return parsed


@router.post("/raw", response_model=ParsedJobResponse)
def parse_raw_job(payload: RawJobParseRequest):
    parsed = parse_job_description(
        title=payload.title,
        company=payload.company,
        location=payload.location,
        description=payload.description,
    )

    return parsed