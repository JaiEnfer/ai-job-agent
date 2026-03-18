from urllib.parse import urlparse


def detect_job_site(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower()

    if "linkedin.com" in hostname:
        return "linkedin"
    if "stepstone." in hostname:
        return "stepstone"
    if "indeed." in hostname:
        return "indeed"

    return "generic"