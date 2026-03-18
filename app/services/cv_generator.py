from typing import List


def build_tailored_summary(
    full_name: str,
    headline: str,
    summary: str,
    matched_skills: List[str],
    target_job_title: str,
    target_company: str,
) -> str:
    matched_skills_text = ", ".join(matched_skills[:6]) if matched_skills else "relevant technical skills"

    base_summary_parts = []

    if headline:
        base_summary_parts.append(headline.strip())

    if summary:
        base_summary_parts.append(summary.strip())

    base_summary = " ".join(base_summary_parts).strip()

    tailored = (
        f"{full_name} is a strong candidate for the {target_job_title} role at {target_company}. "
        f"Profile alignment is strongest around {matched_skills_text}. "
    )

    if base_summary:
        tailored += base_summary

    return tailored.strip()


def build_prioritized_skills(
    matched_skills: List[str],
    profile_skills: List[str],
    missing_skills: List[str],
) -> List[str]:
    prioritized = []

    for skill in matched_skills:
        if skill not in prioritized:
            prioritized.append(skill)

    for skill in profile_skills:
        if skill not in prioritized:
            prioritized.append(skill)

    for skill in missing_skills[:3]:
        label = f"{skill} (gap to address)"
        if label not in prioritized:
            prioritized.append(label)

    return prioritized[:12]


def split_text_to_points(text: str) -> List[str]:
    if not text:
        return []

    separators = ["\n", ".", ";"]
    chunks = [text]

    for sep in separators:
        new_chunks = []
        for chunk in chunks:
            new_chunks.extend(chunk.split(sep))
        chunks = new_chunks

    cleaned = [chunk.strip() for chunk in chunks if chunk.strip()]
    return cleaned


def build_tailored_experience_bullets(
    experience_text: str,
    matched_skills: List[str],
    missing_skills: List[str],
) -> List[str]:
    raw_points = split_text_to_points(experience_text)

    bullets = []

    for point in raw_points:
        point_lower = point.lower()

        if any(skill.lower() in point_lower for skill in matched_skills):
            bullets.append(point)

    if not bullets:
        bullets = raw_points[:4]

    enhanced_bullets = []
    for bullet in bullets[:6]:
        enhanced_bullets.append(f"Demonstrated experience relevant to the target role: {bullet}")

    if missing_skills:
        enhanced_bullets.append(
            f"Tailoring opportunity: strengthen evidence for {', '.join(missing_skills[:3])} in project and experience bullets."
        )

    return enhanced_bullets[:6]


def build_prioritized_projects(projects_text: str, matched_skills: List[str]) -> List[str]:
    if not projects_text:
        return []

    raw_projects = []
    for part in projects_text.split(","):
        cleaned = part.strip()
        if cleaned:
            raw_projects.append(cleaned)

    prioritized = []

    for project in raw_projects:
        project_lower = project.lower()
        if any(skill.lower() in project_lower for skill in matched_skills):
            prioritized.append(project)

    if not prioritized:
        prioritized = raw_projects[:4]

    return prioritized[:4]


def build_improvement_suggestions(
    missing_skills: List[str],
    language_match: bool,
    visa_match: bool,
    location_match: bool,
) -> List[str]:
    suggestions = []

    if missing_skills:
        suggestions.append(
            f"Add stronger evidence for these missing skills if truthful: {', '.join(missing_skills[:5])}."
        )

    if not language_match:
        suggestions.append(
            "Adjust CV and application materials to address language requirements clearly."
        )

    if not visa_match:
        suggestions.append(
            "Address work authorization or visa sponsorship needs clearly in the application strategy."
        )

    if not location_match:
        suggestions.append(
            "Clarify relocation flexibility or Germany location preference in the CV or cover letter."
        )

    if not suggestions:
        suggestions.append("Profile appears well aligned; focus on concise, ATS-friendly presentation.")

    return suggestions