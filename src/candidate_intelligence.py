from __future__ import annotations

import logging
from typing import Any

from .candidate_text import candidate_to_text
from .ontology import find_ontology_matches, map_skill
from .utils import normalize_text, safe_get, unique_preserve_order

logger = logging.getLogger(__name__)

SERVICE_OR_CONSULTING_TERMS = (
    "consulting",
    "it services",
    "outsourcing",
    "systems integrator",
    "managed services",
    "professional services",
)
PRODUCT_TERMS = (
    "product",
    "saas",
    "platform",
    "marketplace",
    "consumer internet",
    "fintech",
    "hrtech",
    "healthtech",
    "edtech",
    "ecommerce",
)
STARTUP_TERMS = ("startup", "founding", "early-stage", "seed", "series a", "series b")
LEADERSHIP_TERMS = ("led", "owned", "drove", "architected", "mentored", "managed", "hired", "principal", "staff", "lead")
RETRIEVAL_TERMS = ("retrieval", "semantic search", "vector search", "embeddings", "ann", "faiss", "bm25", "search")
RANKING_TERMS = ("ranking", "ranker", "learning to rank", "ltr", "re-rank", "rerank", "ndcg", "mrr", "map")
RECOMMENDATION_TERMS = ("recommendation", "recommender", "personalization", "collaborative filtering", "candidate matching")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(term) in normalized for term in terms)


def extract_technical_domains(candidate_json: dict[str, Any]) -> list[str]:
    text = candidate_to_text(candidate_json)
    matches = find_ontology_matches(text)
    return unique_preserve_order(match["domain"] for match in matches if match["domain"] != "unknown")


def extract_career_patterns(candidate_json: dict[str, Any]) -> list[str]:
    text = candidate_to_text(candidate_json)
    profile = candidate_json.get("profile", {}) or {}
    career_history = candidate_json.get("career_history", []) or []
    patterns: list[str] = []

    if _contains_any(text, SERVICE_OR_CONSULTING_TERMS):
        patterns.append("services_or_consulting_exposure")
    if _contains_any(text, PRODUCT_TERMS):
        patterns.append("product_or_platform_exposure")
    if _contains_any(text, STARTUP_TERMS):
        patterns.append("startup_exposure")

    durations = [
        int(role.get("duration_months", 0))
        for role in career_history
        if isinstance(role, dict) and str(role.get("duration_months", "")).isdigit()
    ]
    if durations:
        avg_tenure = sum(durations) / len(durations)
        if avg_tenure < 18:
            patterns.append("short_average_tenure")
        elif avg_tenure >= 36:
            patterns.append("stable_tenure")

    years = float(profile.get("years_of_experience") or 0)
    if years >= 5:
        patterns.append("senior_experience_band")
    elif years > 0:
        patterns.append("early_or_mid_experience_band")
    return unique_preserve_order(patterns)


def candidate_profile_summary(candidate_json: dict[str, Any]) -> str:
    profile = candidate_json.get("profile", {}) or {}
    title = profile.get("current_title", "Unknown title")
    years = profile.get("years_of_experience", 0)
    industry = profile.get("current_industry", "unknown industry")
    headline = profile.get("headline", "")
    return f"{title} with {years} years of experience in {industry}. {headline}".strip()


def _skill_categories(candidate_json: dict[str, Any]) -> list[str]:
    categories: list[str] = []
    for skill in candidate_json.get("skills", []) or []:
        if not isinstance(skill, dict):
            continue
        mapped = map_skill(str(skill.get("name", "")))
        if mapped["category"] != "unknown":
            categories.append(mapped["category"])
    return unique_preserve_order(categories)


def _leadership_indicators(candidate_json: dict[str, Any]) -> list[str]:
    text = candidate_to_text(candidate_json)
    normalized = normalize_text(text)
    return unique_preserve_order(term for term in LEADERSHIP_TERMS if term in normalized)


def _product_company_experience(candidate_json: dict[str, Any]) -> bool:
    text = candidate_to_text(candidate_json)
    profile_industry = normalize_text(safe_get(candidate_json, ["profile", "current_industry"]))
    has_product = _contains_any(text, PRODUCT_TERMS)
    only_service_current = any(term in profile_industry for term in SERVICE_OR_CONSULTING_TERMS)
    return has_product or not only_service_current


def _startup_experience(candidate_json: dict[str, Any]) -> bool:
    text = candidate_to_text(candidate_json)
    if _contains_any(text, STARTUP_TERMS):
        return True
    for role in candidate_json.get("career_history", []) or []:
        if not isinstance(role, dict):
            continue
        if role.get("company_size") in {"1-10", "11-50", "51-200"}:
            return True
    return False


def extract_candidate_intelligence(candidate_json: dict[str, Any]) -> dict[str, Any]:
    text = candidate_to_text(candidate_json)
    technical_domains = extract_technical_domains(candidate_json)
    skill_categories = _skill_categories(candidate_json)
    intelligence = {
        "candidate_id": candidate_json.get("candidate_id", ""),
        "technical_domains": technical_domains,
        "skill_categories": skill_categories,
        "career_patterns": extract_career_patterns(candidate_json),
        "experience_years": float(safe_get(candidate_json, ["profile", "years_of_experience"], 0) or 0),
        "leadership_indicators": _leadership_indicators(candidate_json),
        "retrieval_experience": _contains_any(text, RETRIEVAL_TERMS),
        "ranking_experience": _contains_any(text, RANKING_TERMS),
        "recommendation_experience": _contains_any(text, RECOMMENDATION_TERMS),
        "product_company_experience": _product_company_experience(candidate_json),
        "startup_experience": _startup_experience(candidate_json),
        "career_summary": candidate_profile_summary(candidate_json),
    }
    logger.debug("Candidate intelligence for %s: %s", intelligence["candidate_id"], intelligence)
    return intelligence

