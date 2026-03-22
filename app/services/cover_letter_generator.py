from typing import List


def build_opening_paragraph(
    full_name: str,
    target_job_title: str,
    target_company: str,
    language: str = "english",
) -> str:
    if language.strip().lower() == "german":
        return (
            f"Sehr geehrtes Einstellungsteam bei {target_company},\n\n"
            f"hiermit bewerbe ich mich mit großem Interesse auf die Stelle als {target_job_title}. "
            f"Mein Hintergrund in KI-Engineering, Backend-Systemen und praxisorientierter Produktentwicklung macht diese Position besonders attraktiv für mich."
        )
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
    language: str = "english",
) -> str:
    is_german = language.strip().lower() == "german"

    if is_german:
        location_text = f" Besonders interessiere ich mich für Möglichkeiten in {preferred_locations}." if preferred_locations else ""
        base = (
            f"Was mich an dieser Möglichkeit bei {target_company} besonders anspricht, ist die Chance, in einer Rolle als {target_job_title} einen Beitrag zu leisten. "
            f"Ich bin motiviert, praxisnahe, wirkungsvolle Systeme zu entwickeln, die maschinelles Lernen und Software-Engineering verbinden."
        )
    else:
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
    language: str = "english",
) -> str:
    is_german = language.strip().lower() == "german"
    matched_text = ", ".join(matched_skills[:8]) if matched_skills else (
        "relevante technische Fähigkeiten" if is_german else "relevant technical capabilities"
    )

    if is_german:
        fit = f"Mein Hintergrund ist besonders relevant in den Bereichen {matched_text}. "
        if missing_skills:
            fit += (
                f"Ich bin außerdem bereit, meine Kenntnisse in Bereichen wie "
                f"{', '.join(missing_skills[:3])} bei Bedarf zu vertiefen."
            )
    else:
        fit = f"My background is especially relevant in the areas of {matched_text}. "
        if missing_skills:
            fit += (
                f"I am also prepared to strengthen my exposure to areas such as "
                f"{', '.join(missing_skills[:3])} where needed."
            )

    return fit.strip()


def build_closing_paragraph(
    target_company: str,
    visa_status: str,
    work_authorization: str,
    language: str = "english",
) -> str:
    # Only include visa/auth text if it's short and clean (not raw CV dump)
    combined = f"{visa_status or ''} {work_authorization or ''}".strip()
    combined = combined if len(combined) < 120 else ""

    if language.strip().lower() == "german":
        visa_text = f" {combined}." if combined else ""
        return (
            f"Ich würde mich sehr freuen, bei {target_company} mitzuwirken und in einem persönlichen Gespräch zu erläutern, "
            f"wie mein technischer Hintergrund und meine Motivation zu Ihren Anforderungen passen.{visa_text} "
            f"Vielen Dank für Ihre Zeit und Ihr Interesse."
        )

    visa_text = f" {combined}." if combined else ""
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
    language: str = "english",
) -> str:
    sign_off = "Mit freundlichen Grüßen," if language.strip().lower() == "german" else "Sincerely,"
    return (
        f"{opening_paragraph}\n\n"
        f"{motivation_paragraph}\n\n"
        f"{fit_paragraph}\n\n"
        f"{closing_paragraph}\n\n"
        f"{sign_off}\n"
        f"{full_name}"
    )