from __future__ import annotations

from typing import Any

from .utils import safe_get


def _join(values: list[str]) -> str:
    return "; ".join(value for value in values if value)


def candidate_to_text(candidate_json: dict[str, Any]) -> str:
    profile = candidate_json.get("profile", {}) if isinstance(candidate_json, dict) else {}
    career_history = candidate_json.get("career_history", []) or []
    education = candidate_json.get("education", []) or []
    skills = candidate_json.get("skills", []) or []

    skill_text = _join(
        [
            f"{skill.get('name', '')} ({skill.get('proficiency', 'unspecified')}, {skill.get('duration_months', 0)} months)"
            for skill in skills
            if isinstance(skill, dict)
        ]
    )

    career_lines: list[str] = []
    for role in career_history:
        if not isinstance(role, dict):
            continue
        career_lines.append(
            " ".join(
                [
                    f"Company: {role.get('company', '')}.",
                    f"Title: {role.get('title', '')}.",
                    f"Industry: {role.get('industry', '')}.",
                    f"Company size: {role.get('company_size', '')}.",
                    f"Duration months: {role.get('duration_months', '')}.",
                    f"Description: {role.get('description', '')}.",
                ]
            )
        )

    education_text = _join(
        [
            f"{item.get('degree', '')} in {item.get('field_of_study', '')} from {item.get('institution', '')} ({item.get('tier', 'unknown')})"
            for item in education
            if isinstance(item, dict)
        ]
    )

    sections = [
        f"Candidate ID: {candidate_json.get('candidate_id', '')}",
        f"Headline: {safe_get(candidate_json, ['profile', 'headline'])}",
        f"Summary: {safe_get(candidate_json, ['profile', 'summary'])}",
        f"Current title: {safe_get(candidate_json, ['profile', 'current_title'])}",
        f"Current company: {safe_get(candidate_json, ['profile', 'current_company'])}",
        f"Current industry: {safe_get(candidate_json, ['profile', 'current_industry'])}",
        f"Years of experience: {safe_get(candidate_json, ['profile', 'years_of_experience'], 0)}",
        f"Location: {safe_get(candidate_json, ['profile', 'location'])}, {safe_get(candidate_json, ['profile', 'country'])}",
        f"Skills: {skill_text}",
        f"Career history: {' '.join(career_lines)}",
        f"Education: {education_text}",
    ]
    return "\n".join(section for section in sections if section.strip())

