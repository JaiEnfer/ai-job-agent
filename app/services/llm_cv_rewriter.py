from app.core.config import settings
from app.services.llm_text import generate_text


def rewrite_cv_as_recruiter(
    job_title: str,
    job_company: str,
    job_location: str | None,
    job_description: str,
    full_name: str,
    headline: str,
    summary: str,
    skills: str,
    experience: str,
    projects: str,
    prompt: str | None = None,
) -> str:
    """Rewrite a candidate CV as if you were a senior recruiter screening 200+ applicants.

    Uses the LLM to rewrite the candidate's profile into a concise, ATS-friendly CV.

    Falls back to a simple text-based output if the model key is missing or an error occurs.
    """

    prompt = prompt or settings.LLM_CV_REWRITE_PROMPT
    if not prompt:
        prompt = f"""
You are a senior technical recruiter in Germany who reviews over 200 applications for the same role.
Given the job and the candidate profile below, rewrite the candidate's CV so it is concise, highly tailored, and written as if it will be read by a busy hiring manager and an ATS system.

Job:
- Title: {job_title}
- Company: {job_company}
- Location: {job_location or 'N/A'}

Job Description:
{job_description}

Candidate Profile:
- Name: {full_name}
- Headline: {headline}
- Summary: {summary}
- Skills: {skills}
- Experience: {experience}
- Projects: {projects}

Instructions:
- Output only the rewritten CV (no commentary).
- Use bullets and short paragraphs.
- Focus on measurable impact and relevant skills.
- Remove unrelated or generic content.
- Keep it within 1-2 pages of text.
""".strip()

    try:
        return generate_text(prompt)
    except Exception:
        # Fallback: build a basic summary-like CV if LLM is unavailable
        parts = [
            f"{full_name} - {headline}",
            "\nSummary:\n" + (summary or ""),
            "\nKey Skills:\n" + (skills or ""),
            "\nExperience:\n" + (experience or ""),
            "\nProjects:\n" + (projects or ""),
        ]
        return "\n".join([p for p in parts if p.strip()])
