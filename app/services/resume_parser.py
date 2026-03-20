import re
from html.parser import HTMLParser
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    from pdf2image import convert_from_bytes
    import pytesseract
except ImportError:  # pragma: no cover
    convert_from_bytes = None
    pytesseract = None

EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\+?[\d\s\-\.\(\)]+\d")
URL_REGEX = re.compile(r"(?:https?://)?(?:www\.)?[A-Za-z0-9\-_.]+\.[A-Za-z]{2,}(?:/[^\s<>]*)?")
MAILTO_REGEX = re.compile(r"mailto:([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})", re.IGNORECASE)
TEL_REGEX = re.compile(r"tel:([\d\s\-\.\(\)]+)", re.IGNORECASE)

# Matches shorthand LinkedIn/GitHub handles used in CVs without a full URL.
# e.g. "Linkedin jai-prakash-data-scientist" or "Linkedinjai-prakash-data-scientist"
LINKEDIN_SHORTHAND_REGEX = re.compile(
    r"linkedin\s*[:/]?\s*([\w\-]+(?:/[\w\-]+)*)", re.IGNORECASE
)
GITHUB_SHORTHAND_REGEX = re.compile(
    r"github\s*[:/]?\s*([\w\-]+)", re.IGNORECASE
)


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "meta":
            data = {k.lower(): v for k, v in attrs}
            if data.get("name") == "description" and data.get("content"):
                self.description = data["content"].strip()

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data.strip()


def _fetch_url_metadata(url: str, timeout: int = 5) -> Dict[str, str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read(100_000).decode(errors="ignore")
    except (HTTPError, URLError, TimeoutError, ValueError):
        return {}

    parser = _MetaParser()
    parser.feed(body)
    return {k: v for k, v in {"title": parser.title, "description": parser.description}.items() if v}


def fetch_url_metadata(url: str, timeout: int = 5) -> Dict[str, str]:
    """Public wrapper to fetch and parse metadata from a URL.

    Adds https:// if missing so that plain domains like "example.com" work.
    """
    url = url.strip()
    if url and not re.match(r"^https?://", url):
        url = f"https://{url}"
    return _fetch_url_metadata(url, timeout=timeout)


def extract_urls(text: str) -> List[str]:
    urls = {u.strip().rstrip(".,;") for u in URL_REGEX.findall(text)}
    return [u for u in urls if "@" not in u]


def _clean_url(url: str) -> str:
    url = url.strip().rstrip(".,;")
    if url.startswith("www."):
        return f"https://{url}"
    if re.match(r"^[A-Za-z0-9\-]{2,}\.[A-Za-z]{2,}($|/)", url):
        return f"https://{url}"
    return url


def _extract_linkedin_shorthand(text: str) -> Optional[str]:
    """Extract LinkedIn profile URL from shorthand like 'Linkedinjai-prakash-data-scientist'."""
    match = LINKEDIN_SHORTHAND_REGEX.search(text)
    if match:
        handle = match.group(1).strip().strip("/")
        # Avoid matching the word "linkedin" followed by an email or noise
        if "@" not in handle and len(handle) > 2:
            return f"https://linkedin.com/in/{handle}"
    return None


def _extract_github_shorthand(text: str) -> Optional[str]:
    """Extract GitHub profile URL from shorthand like 'GithubJaiEnfer'."""
    match = GITHUB_SHORTHAND_REGEX.search(text)
    if match:
        handle = match.group(1).strip()
        if "@" not in handle and len(handle) > 1:
            return f"https://github.com/{handle}"
    return None


def extract_profile_links(text: str, extra_urls: Optional[List[str]] = None) -> Dict[str, str]:
    urls = extract_urls(text)

    # Try compacted version for spaced-out URLs
    compact = re.sub(r"\s+", "", text)
    urls.extend(extract_urls(compact))

    if extra_urls:
        urls.extend(extra_urls)

    profile_links: Dict[str, str] = {}

    for url in urls:
        url = _clean_url(url)
        lower = url.lower()

        if "linkedin.com" in lower and "in/" in lower:
            profile_links.setdefault("linkedin_url", url)
        elif "github.com" in lower:
            profile_links.setdefault("github_url", url)
        elif "behance.net" in lower or "dribbble.com" in lower or "portfolio" in lower:
            profile_links.setdefault("portfolio_url", url)
        elif lower.startswith("mailto:"):
            match = MAILTO_REGEX.search(url)
            if match:
                profile_links.setdefault("email", match.group(1))
        elif lower.startswith("tel:"):
            match = TEL_REGEX.search(url)
            if match:
                profile_links.setdefault("phone", match.group(1))
        elif "http" in lower and "linkedin" not in lower and "github" not in lower and "portfolio" not in lower:
            profile_links.setdefault("portfolio_url", url)

    # Fall back to shorthand extraction if full URLs were not found
    if "linkedin_url" not in profile_links:
        linkedin = _extract_linkedin_shorthand(text)
        if linkedin:
            profile_links["linkedin_url"] = linkedin

    if "github_url" not in profile_links:
        github = _extract_github_shorthand(text)
        if github:
            profile_links["github_url"] = github

    return profile_links


def _collapse_spaced_letters(text: str) -> str:
    """Collapse sequences like 'e n g i n e e r' from poor PDF extraction.

    Requires 4+ consecutive single letters to avoid merging legitimate
    short words (e.g. 'a b' or 'I O') that appear in skill lists.
    """
    segments = re.split(r"\s{2,}", text)
    collapsed_segments = []

    for seg in segments:
        # Only collapse runs of 4 or more spaced single letters
        seg = re.sub(r"\b(?:[A-Za-z]\s+){3,}[A-Za-z]\b", lambda m: m.group(0).replace(" ", ""), seg)
        collapsed_segments.append(seg.strip())

    return " ".join([s for s in collapsed_segments if s])


def _split_concatenated_fields(text: str) -> str:
    """Insert spaces between known concatenated fields that PDFs often merge.

    Handles patterns like:
      - 'prakashjai990@gmail.comLinkedinjai'   -> 'prakashjai990@gmail.com Linkedin jai'
      - 'GithubJaiEnfer'                       -> 'Github JaiEnfer'
    """
    # Split email from any immediately following uppercase text
    text = re.sub(r"([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})([A-Z])", r"\1 \2", text)

    # Insert space before known CV section/contact keywords when merged with prior content
    keywords = [
        "Linkedin", "Github", "Profile", "Skills", "Experience",
        "Education", "Projects", "Certifications", "Languages",
        "Summary", "Objective", "Employment",
    ]
    for kw in keywords:
        text = re.sub(rf"([^\s])({kw})", rf"\1 \2", text)

    return text


def _normalize_text(text: str) -> str:
    """Normalize extracted text while preserving line structure for section detection."""
    # Normalize line endings.
    text = re.sub(r"\r\n|\r", "\n", text)

    # Remove PDF icon placeholders (cid:###).
    text = re.sub(r"\(cid:\d+\)", "", text)

    # Remove common CV icon/symbol characters from icon fonts that PDF extractors
    # produce as noise (e.g. location pin, phone, envelope icons).
    text = re.sub(r"[\u0230\u041b\u2600-\u26ff\u2700-\u27bf\uf000-\uffff]", " ", text)

    # Replace bullet-like separators with newline to preserve structure.
    text = re.sub(r"[·•–—|\u2022\u2023\u25E6\u2043\u2219]", "\n", text)

    # Split concatenated fields before further processing.
    text = _split_concatenated_fields(text)

    # Process line by line — collapse spaced letters but keep line breaks intact.
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = _collapse_spaced_letters(line).strip()
        # Collapse multiple spaces within a line into one.
        line = re.sub(r" {2,}", " ", line)
        if line:
            cleaned_lines.append(line)

    # Collapse runs of 3+ blank lines into a single blank line.
    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def _match_label(text: str, patterns: List[str]) -> Optional[str]:
    for pat in patterns:
        match = re.search(pat, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _ocr_pdf_text(file: UploadFile) -> str:
    """OCR-based fallback for PDFs when text extraction fails."""
    if not (convert_from_bytes and pytesseract):
        return ""

    file.file.seek(0)
    data = file.file.read()
    try:
        images = convert_from_bytes(data, dpi=200)
    except Exception:
        return ""

    texts: List[str] = []
    for image in images:
        try:
            texts.append(pytesseract.image_to_string(image, lang="eng"))
        except Exception:
            continue

    return _normalize_text("\n".join(texts))


def _extract_text_from_pdf(file: UploadFile) -> str:
    file.file.seek(0)

    # Prefer pdfplumber for better layout text extraction when available.
    if pdfplumber:
        try:
            with pdfplumber.open(file.file) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            extracted = _normalize_text("\n".join(pages))
            cid_count = extracted.count("(cid:")
            word_count = max(len(extracted.split()), 1)
            if len(extracted) > 50 and (cid_count == 0 or cid_count / word_count < 0.1):
                return extracted
        except Exception:
            file.file.seek(0)

    # Fallback to PyPDF2.
    try:
        file.file.seek(0)
        reader = PdfReader(file.file)
        pages_text = "\n".join((page.extract_text() or "") for page in reader.pages)
        extracted = _normalize_text(pages_text)
        cid_count = extracted.count("(cid:")
        word_count = max(len(extracted.split()), 1)
        if len(extracted) > 50 and (cid_count == 0 or cid_count / word_count < 0.1):
            return extracted
    except Exception:
        pass

    # Last resort: OCR.
    return _ocr_pdf_text(file)


def extract_pdf_links(file: UploadFile) -> List[str]:
    """Extract hyperlinks (URI / mailto / tel) from a PDF file's annotations."""
    file.file.seek(0)
    urls: List[str] = []

    try:
        reader = PdfReader(file.file)
        for page in reader.pages:
            annots = page.get("/Annots")
            if not annots:
                continue
            for annot in annots:
                obj = annot.get_object()
                if not isinstance(obj, dict):
                    continue
                action = obj.get("/A")
                if action and isinstance(action, dict):
                    uri = action.get("/URI")
                    if uri:
                        urls.append(str(uri))
                elif obj.get("/URI"):
                    urls.append(str(obj.get("/URI")))
    except Exception:
        return []

    return urls


def _extract_text_from_docx(file: UploadFile) -> str:
    file.file.seek(0)
    doc = Document(file.file)
    return _normalize_text("\n".join(p.text for p in doc.paragraphs))


def extract_docx_links(file: UploadFile) -> List[str]:
    """Extract hyperlinks stored in a .docx file."""
    file.file.seek(0)
    try:
        doc = Document(file.file)
        urls: List[str] = []
        for rel in doc.part.rels.values():
            if "hyperlink" in rel.reltype:
                urls.append(rel.target_ref)
        return urls
    except Exception:
        return []


def _extract_text_from_txt(file: UploadFile) -> str:
    file.file.seek(0)
    raw = file.file.read()
    if isinstance(raw, bytes):
        raw = raw.decode(errors="ignore")
    return _normalize_text(raw)


def extract_text_from_resume(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        return _extract_text_from_pdf(file)
    if filename.endswith(".docx"):
        return _extract_text_from_docx(file)
    if filename.endswith(".txt"):
        return _extract_text_from_txt(file)
    try:
        return _extract_text_from_txt(file)
    except Exception:
        return ""


def extract_links_from_resume(file: UploadFile) -> List[str]:
    """Extract any embedded URL / mailto / tel links from a resume file."""
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        return extract_pdf_links(file)
    if filename.endswith(".docx"):
        return extract_docx_links(file)
    return []


def extract_email(text: str) -> Optional[str]:
    mailto = MAILTO_REGEX.search(text)
    if mailto:
        return mailto.group(1)

    compact = re.sub(r"\s+", "", text)

    email = _match_label(text, [r"email\s*[:\-]\s*(\S+@\S+)", r"e-?mail\s*[:\-]\s*(\S+@\S+)"])
    if email:
        return email

    match = EMAIL_REGEX.search(compact)
    if match:
        return match.group(0)

    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    tel = TEL_REGEX.search(text)
    if tel:
        return tel.group(1)

    compact = re.sub(r"\s+", "", text)

    labeled = _match_label(text, [
        r"(?:phone|tel|mobile|cell)\s*[:\-]\s*([+\d][\d\s\-\.\(\)]+)",
        r"(?:phone|tel|mobile|cell)\s*[:\-]\s*(\d[\d\s\-\.\(\)]+)",
    ])
    if labeled:
        return labeled

    match = PHONE_REGEX.search(compact)
    if not match:
        match = PHONE_REGEX.search(text)
        if not match:
            return None

    number = match.group(0)
    digits = re.sub(r"\D", "", number)
    if len(digits) < 7:
        return None

    return re.sub(r"\s+", " ", number).strip()


def _truncate_string(value: str, max_length: int) -> str:
    return value.strip()[:max_length] if value else value


def extract_name(text: str) -> Optional[str]:
    text = _normalize_text(text)

    name_label = _match_label(text, [r"name\s*[:\-]\s*(.+)"])
    if name_label:
        return _truncate_string(name_label, 255)

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:12]:
        lower = line.lower()
        if any(token in lower for token in [
            "email", "e-?mail", "phone", "tel", "linkedin", "github", "resume", "cv",
            "profile", "summary", "experience", "education", "skills",
        ]):
            continue

        words = line.split()
        if 2 <= len(words) <= 5:
            cap_count = sum(1 for w in words if w and w[0].isupper())
            if cap_count >= len(words) - 1:
                return _truncate_string(line, 255)

    if lines:
        first_line = lines[0]
        words = first_line.split()
        if len(words) >= 2:
            return _truncate_string(" ".join(words[:3]), 255)

    return None


def extract_location(text: str) -> Optional[str]:
    text = _normalize_text(text)

    location = _match_label(text, [
        r"location\s*[:\-]\s*(.+)",
        r"address\s*[:\-]\s*(.+)",
        r"city\s*[:\-]\s*(.+)",
        r"based in\s+([^\n]+)",
    ])
    if location:
        return _truncate_string(location, 255)

    non_location_tokens = [
        "email", "phone", "tel", "linkedin", "github", "www.",
        "experience", "education", "skills", "university", "college",
        "bachelor", "master", "http",
    ]
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) > 80:
            continue
        lower = line.lower()
        if any(token in lower for token in non_location_tokens):
            continue
        # Match "City, Country" or "City, State" style patterns.
        if re.search(r"[A-Za-z\s\-]{2,},\s*[A-Za-z\s]{2,}", line):
            return _truncate_string(line, 255)

    return None


def parse_resume_sections(text: str) -> dict[str, str]:
    """Parse common resume sections by heading keywords.

    Line structure must be preserved in the input text.
    """
    normalized = text

    headings = {
        "summary": [r"summary", r"professional summary", r"profile", r"about me", r"objective"],
        "skills": [r"skills", r"technical skills", r"skillset", r"core competencies"],
        "experience": [r"experience", r"work experience", r"professional experience", r"employment history"],
        "education": [r"education", r"academic background", r"qualifications"],
        "projects": [r"projects", r"selected projects", r"key projects"],
        "certifications": [r"certifications", r"certificates", r"licenses"],
        "languages": [r"languages", r"language skills", r"spoken languages"],
    }

    heading_pattern = r"^\s*(?P<heading>" + "|".join(
        f"(?:{pattern})" for patterns in headings.values() for pattern in patterns
    ) + r")\s*[:\-]?\s*$"
    heading_re = re.compile(heading_pattern, flags=re.IGNORECASE | re.MULTILINE)

    matches = list(heading_re.finditer(normalized))
    if not matches:
        return {}

    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        name = match.group("heading").strip().lower()
        section_key = None
        for key, patterns in headings.items():
            if any(re.fullmatch(pat, name, flags=re.IGNORECASE) for pat in patterns):
                section_key = key
                break
        if not section_key:
            continue

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
        content = normalized[start:end].strip()
        content = "\n".join(line.lstrip("-•* ") for line in content.splitlines())
        sections[section_key] = content

    return sections