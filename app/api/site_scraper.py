from fastapi import APIRouter, HTTPException

from app.schemas.site_scraper import SiteScrapeRequest, SiteScrapeResponse
from app.services.scrapers.site_extractors import extract_job_text_from_site

router = APIRouter(prefix="/site-scraper", tags=["site-scraper"])


@router.post("/job-page", response_model=SiteScrapeResponse)
def scrape_site_aware_job_page(payload: SiteScrapeRequest):
    try:
        result = extract_job_text_from_site(str(payload.url))
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Site-aware scraping failed: {str(exc)}")