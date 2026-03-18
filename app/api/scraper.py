from fastapi import APIRouter, HTTPException

from app.schemas.scraper import ScrapeJobPageRequest, ScrapeJobPageResponse
from app.services.scrapers.job_page_scraper import scrape_job_page

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/job-page", response_model=ScrapeJobPageResponse)
def scrape_job_page_endpoint(payload: ScrapeJobPageRequest):
    try:
        result = scrape_job_page(str(payload.url))
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(exc)}")