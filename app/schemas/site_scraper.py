from pydantic import BaseModel, HttpUrl


class SiteScrapeRequest(BaseModel):
    url: HttpUrl


class SiteScrapeResponse(BaseModel):
    site_name: str
    source_url: str
    page_title: str
    raw_text: str
    used_selector_strategy: bool
    selector_block_count: int
    text_length: int