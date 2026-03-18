from typing import List


def build_opening_paragraph(full_name: str, target_job_title: str, target_company: str) -> str:
    return (
        f"Dear Hiring Team at {target_company},\n\n"
        f"I am excited to apply for the {target_job_title} position. "
        f"My background in AI engineering, backend systems, and practical product-focused development makes this role especially compelling to me."
    )


def build_motivation_paragraph(
    target_job_title: str,
    target_company: str,
    summary: str,
    preferred_locations: str,
) -> str:
    location_text = f" I am particularly interested in opportunities in {preferred_locations}." if preferred_locations else ""

    base = (
        f"What particularly attracts me to this opportunity at {target_company} is the chance to contribute to a role focused on {target_job_title}. "
        f"I am motivated by building practical, high-impact systems that connect machine learning and software engineering."
    )

    if summary:
        base += f" {summary.strip()}"

    return base + location_text


def build_fit_paragraph(
    matched_skills: List[str],
    missing_skills: List[str],
    experience: str,
    projects: str,
) -> str:
    matched_text = ", ".join(matched_skills[:8]) if matched_skills else "relevant technical capabilities"

    fit = (
        f"My background is especially relevant in the areas of {matched_text}. "
    )

    if experience:
        fit += f"{experience.strip()} "

    if projects:
        fit += f"In addition, projects such as {projects.strip()} demonstrate my ability to apply these skills in practice. "

    if missing_skills:
        fit += (
            f"I am also prepared to strengthen my exposure to areas such as {', '.join(missing_skills[:3])} where needed."
        )

    return fit.strip()


def build_closing_paragraph(target_company: str, visa_status: str, work_authorization: str) -> str:
    visa_text = ""

    combined = f"{visa_status or ''} {work_authorization or ''}".strip()
    if combined:
        visa_text = f" {combined}."

    return (
        f"I would welcome the opportunity to contribute to {target_company} and discuss how my technical background and motivation align with your needs.{visa_text} "
        f"Thank you for your time and consideration."
    )


def build_improvement_notes(
    missing_skills: List[str],
    language_match: bool,
    visa_match: bool,
    location_match: bool,
) -> List[str]:
    notes = []

    if missing_skills:
        notes.append(
            f"Consider adding concrete examples that demonstrate: {', '.join(missing_skills[:5])}."
        )

    if not language_match:
        notes.append("Address language readiness more clearly in the letter.")

    if not visa_match:
        notes.append("Explain work authorization or sponsorship need carefully and professionally.")

    if not location_match:
        notes.append("Mention relocation flexibility or Germany location preference explicitly.")

    if not notes:
        notes.append("Cover letter alignment looks strong for this role.")

    return notes


def build_full_cover_letter(
    full_name: str,
    opening_paragraph: str,
    motivation_paragraph: str,
    fit_paragraph: str,
    closing_paragraph: str,
) -> str:
    return (
        f"{opening_paragraph}\n\n"
        f"{motivation_paragraph}\n\n"
        f"{fit_paragraph}\n\n"
        f"{closing_paragraph}\n\n"
        f"Sincerely,\n"
        f"{full_name}"
    )