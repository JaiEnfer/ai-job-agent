from pydantic import BaseModel, HttpUrl

from app.schemas.job import JobResponse
from app.schemas.job_parser import ParsedJobResponse


class ScrapeAndIngestRequest(BaseModel):
    url: HttpUrl
    source: str | None = None
    company: str | None = None
    location: str | None = None


class ScrapeAndIngestResponse(BaseModel):
    stored_job: JobResponse
    parsed_job: ParsedJobResponse
    scraped_page_title: str
    scraped_source_url: str