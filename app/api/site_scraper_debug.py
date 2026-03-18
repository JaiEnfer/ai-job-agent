from fastapi import APIRouter, HTTPException

from app.schemas.site_scraper import SiteScrapeRequest
from app.services.scrapers.site_extractors import extract_job_text_from_site

router = APIRouter(prefix="/site-scraper-debug", tags=["site-scraper-debug"])


@router.post("/job-page")
def scrape_site_aware_job_page_debug(payload: SiteScrapeRequest):
    try:
        result = extract_job_text_from_site(str(payload.url))
        preview = result["raw_text"][:2000]

        return {
            "site_name": result["site_name"],
            "source_url": result["source_url"],
            "page_title": result["page_title"],
            "used_selector_strategy": result["used_selector_strategy"],
            "selector_block_count": result["selector_block_count"],
            "text_length": result["text_length"],
            "raw_text_preview": preview,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Site-aware scraping debug failed: {str(exc)}")