from pydantic import BaseModel, HttpUrl


class ScrapeJobPageRequest(BaseModel):
    url: HttpUrl


class ScrapeJobPageResponse(BaseModel):
    source_url: str
    page_title: str
    raw_text: str
    html_length: int
    text_length: int