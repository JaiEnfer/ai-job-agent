from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.llm_job_parser import LLMParsedJobResponse
from app.services.llm_jd_parser import parse_job_description_with_llm

router = APIRouter(prefix="/llm-job-parser", tags=["llm-job-parser"])


class RawLLMJobParseRequest(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str


@router.get("/{job_id}", response_model=LLMParsedJobResponse)
def parse_job_with_llm(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        parsed = parse_job_description_with_llm(
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
        )
        return parsed
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM parsing failed: {str(exc)}")


@router.post("/raw", response_model=LLMParsedJobResponse)
def parse_raw_job_with_llm(payload: RawLLMJobParseRequest):
    try:
        parsed = parse_job_description_with_llm(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            description=payload.description,
        )
        return parsed
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM raw parsing failed: {str(exc)}")