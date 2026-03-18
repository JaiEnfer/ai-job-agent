from playwright.sync_api import sync_playwright


def fetch_page_content(url: str, wait_until: str = "domcontentloaded", timeout: int = 30000) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until=wait_until, timeout=timeout)
            title = page.title()
            content = page.content()
            final_url = page.url

            return {
                "url": final_url,
                "title": title,
                "html": content,
            }
        finally:
            browser.close()


def fetch_page_with_selectors(
    url: str,
    selectors: list[str],
    wait_until: str = "domcontentloaded",
    timeout: int = 30000,
) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until=wait_until, timeout=timeout)
            title = page.title()
            final_url = page.url
            html = page.content()

            extracted_blocks = []

            for selector in selectors:
                try:
                    locator = page.locator(selector)
                    count = locator.count()

                    for i in range(min(count, 10)):
                        text = locator.nth(i).inner_text().strip()
                        if text:
                            extracted_blocks.append(text)
                except Exception:
                    continue

            return {
                "url": final_url,
                "title": title,
                "html": html,
                "selector_text_blocks": extracted_blocks,
            }
        finally:
            browser.close()