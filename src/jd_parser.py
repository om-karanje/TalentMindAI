from __future__ import annotations

import logging
import re
from typing import Any

from .ontology import find_ontology_matches
from .utils import normalize_text, unique_preserve_order

logger = logging.getLogger(__name__)

MUST_HAVE_CUES = (
    "must have",
    "required",
    "requirements",
    "need",
    "absolutely need",
    "minimum",
    "essential",
)
NICE_TO_HAVE_CUES = (
    "nice to have",
    "preferred",
    "good to have",
    "bonus",
    "plus",
    "would like",
    "desired",
)


def extract_experience(jd_text: str) -> float:
    normalized = normalize_text(jd_text)
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:-|to|and)\s*(\d+(?:\.\d+)?)\s+years",
        r"(\d+(?:\.\d+)?)\s*\+?\s+years",
        r"experience\s*(?:required|of)?\s*:?\s*(\d+(?:\.\d+)?)",
    ]
    values: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, normalized):
            numbers = [float(group) for group in match.groups() if group is not None]
            if numbers:
                values.append(min(numbers))
    return min(values) if values else 0.0


def extract_seniority(jd_text: str) -> str:
    text = normalize_text(jd_text)
    seniority_terms = [
        ("founding", ("founding", "founder", "early team")),
        ("principal", ("principal", "staff", "lead architect")),
        ("senior", ("senior", "sr.", "lead", "tech lead")),
        ("mid", ("mid level", "intermediate", "software engineer ii")),
        ("junior", ("junior", "entry level", "associate", "intern")),
    ]
    for label, terms in seniority_terms:
        if any(term in text for term in terms):
            return label
    return "unspecified"


def extract_domain(jd_text: str) -> str:
    matches = find_ontology_matches(jd_text)
    domains = [match["domain"] for match in matches if match["domain"] != "unknown"]
    if not domains:
        return "general"
    return max(set(domains), key=domains.count)


def extract_skills(jd_text: str) -> list[str]:
    matches = find_ontology_matches(jd_text)
    return unique_preserve_order(match["canonical"] for match in matches)


def _lines_near_cues(jd_text: str, cues: tuple[str, ...]) -> str:
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    selected: list[str] = []
    active = False
    for line in lines:
        normalized = normalize_text(line)
        if any(cue in normalized for cue in cues):
            active = True
            selected.append(line)
            continue
        if active and re.match(r"^[A-Z][A-Za-z0-9 ,/&+-]{2,80}:?$", line):
            active = False
        if active:
            selected.append(line)
    return "\n".join(selected)


def _skills_for_section(jd_text: str, cues: tuple[str, ...]) -> list[str]:
    section = _lines_near_cues(jd_text, cues)
    if not section:
        return []
    return extract_skills(section)


def parse_jd(jd_text: str) -> dict[str, Any]:
    if not jd_text or not jd_text.strip():
        raise ValueError("JD text cannot be empty.")
    must_have = _skills_for_section(jd_text, MUST_HAVE_CUES)
    nice_to_have = _skills_for_section(jd_text, NICE_TO_HAVE_CUES)
    all_skills = extract_skills(jd_text)

    if not must_have:
        must_have = all_skills[:12]
    if not nice_to_have:
        nice_to_have = [skill for skill in all_skills if skill not in must_have][:12]

    parsed = {
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "experience": extract_experience(jd_text),
        "seniority": extract_seniority(jd_text),
        "domain": extract_domain(jd_text),
    }
    logger.debug("Parsed JD: %s", parsed)
    return parsed

