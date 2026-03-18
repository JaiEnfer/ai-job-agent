import re
from html import unescape

from app.services.scrapers.playwright_browser import fetch_page_content


def strip_html_tags(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def scrape_job_page(url: str) -> dict:
    page_data = fetch_page_content(url)

    html = page_data["html"]
    cleaned_text = strip_html_tags(html)

    return {
        "source_url": page_data["url"],
        "page_title": page_data["title"],
        "raw_text": cleaned_text,
        "html_length": len(html),
        "text_length": len(cleaned_text),
    }