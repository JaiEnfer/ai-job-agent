import re
from html import unescape

from app.services.scrapers.playwright_browser import fetch_page_content, fetch_page_with_selectors
from app.services.scrapers.site_detector import detect_job_site


def normalize_text(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def strip_html_tags(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def deduplicate_blocks(blocks: list[str]) -> list[str]:
    seen = set()
    result = []

    for block in blocks:
        normalized = normalize_text(block)
        if normalized and normalized.lower() not in seen:
            seen.add(normalized.lower())
            result.append(normalized)

    return result


def get_site_selectors(site_name: str) -> list[str]:
    selector_map = {
        "linkedin": [
            ".show-more-less-html__markup",
            ".description__text",
            ".jobs-description__content",
            ".jobs-box__html-content",
            "main",
        ],
        "stepstone": [
            '[data-testid="job-description-content"]',
            '[data-testid="job-ad-content"]',
            "main",
            "article",
        ],
        "indeed": [
            "#jobDescriptionText",
            ".jobsearch-JobComponent-description",
            "main",
            "article",
        ],
        "generic": [
            "main",
            "article",
            '[role="main"]',
            ".job-description",
            ".description",
            ".content",
            "body",
        ],
    }

    return selector_map.get(site_name, selector_map["generic"])


def extract_job_text_from_site(url: str) -> dict:
    site_name = detect_job_site(url)
    selectors = get_site_selectors(site_name)

    page_data = fetch_page_with_selectors(url, selectors=selectors)

    selector_blocks = deduplicate_blocks(page_data.get("selector_text_blocks", []))
    selector_text = "\n\n".join(selector_blocks).strip()

    fallback_text = strip_html_tags(page_data.get("html", ""))

    final_text = selector_text if len(selector_text) >= 300 else fallback_text

    return {
        "site_name": site_name,
        "source_url": page_data["url"],
        "page_title": page_data["title"],
        "raw_text": final_text,
        "used_selector_strategy": len(selector_text) >= 300,
        "selector_block_count": len(selector_blocks),
        "text_length": len(final_text),
    }


def extract_job_text_generic(url: str) -> dict:
    page_data = fetch_page_content(url)
    fallback_text = strip_html_tags(page_data.get("html", ""))

    return {
        "site_name": "generic",
        "source_url": page_data["url"],
        "page_title": page_data["title"],
        "raw_text": fallback_text,
        "used_selector_strategy": False,
        "selector_block_count": 0,
        "text_length": len(fallback_text),
    }