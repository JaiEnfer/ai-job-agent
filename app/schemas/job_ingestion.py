from pydantic import BaseModel
from typing import Optional

from app.schemas.job import JobResponse
from app.schemas.job_parser import ParsedJobResponse


class RawJobIngestionRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    job_url: Optional[str] = None
    description: str


class StructuredJobIngestionRequest(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    source: Optional[str] = None
    job_url: Optional[str] = None
    description: str


class JobIngestionResponse(BaseModel):
    stored_job: JobResponse
    parsed_job: ParsedJobResponse