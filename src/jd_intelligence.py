from __future__ import annotations

import logging
from typing import Any

from .jd_parser import extract_skills, parse_jd
from .ontology import find_ontology_matches
from .utils import normalize_text, unique_preserve_order

logger = logging.getLogger(__name__)


HIDDEN_REQUIREMENT_RULES: dict[str, tuple[str, ...]] = {
    "production_deployment_experience": ("production", "deployed", "real users", "at scale", "online"),
    "ranking_or_retrieval_ownership": ("ranking", "retrieval", "search", "recommendation", "matching"),
    "evaluation_maturity": ("ndcg", "mrr", "map", "a/b", "ab test", "benchmark", "offline", "online metric"),
    "hands_on_coding": ("write code", "hands-on", "ship", "build", "implement"),
    "product_judgment": ("product", "workflow", "user", "metric", "feedback loop"),
    "startup_adaptability": ("startup", "founding", "scrappy", "ambiguous", "fast", "changes"),
    "communication_strength": ("write", "async", "documentation", "communicate"),
}

BEHAVIORAL_RULES: dict[str, tuple[str, ...]] = {
    "shipper_mindset": ("ship", "scrappy", "fast", "working", "iterate"),
    "ownership": ("own", "drive", "lead", "mentor", "architecture"),
    "comfortable_with_ambiguity": ("ambiguous", "changes", "from scratch", "unstable"),
    "collaborative_product_thinking": ("pm", "recruiter", "user", "workflow", "feedback"),
    "written_communication": ("write", "async", "documentation"),
}

DISQUALIFIER_RULES: dict[str, tuple[str, ...]] = {
    "pure_research_without_production": ("pure research", "research-only", "academic lab"),
    "keyword_demo_only": ("tutorial", "demo", "recent projects", "framework"),
    "not_recently_hands_on": ("hasn't written production code", "not written production code"),
    "consulting_only_background": ("only worked at consulting", "consulting firms", "services"),
    "wrong_ai_domain_without_ir": ("computer vision", "speech", "robotics", "without", "nlp"),
    "low_external_validation": ("closed-source", "without external validation"),
}

CAREER_PREFERENCE_RULES: dict[str, tuple[str, ...]] = {
    "product_company_background": ("product company", "marketplace", "platform", "saas"),
    "startup_or_growth_stage": ("series", "startup", "founding", "early-stage"),
    "longer_tenure_preferred": ("3+ years", "long term", "stay"),
    "location_or_relocation_fit": ("relocation", "hybrid", "onsite", "office"),
}


def _match_rules(text: str, rules: dict[str, tuple[str, ...]]) -> list[str]:
    normalized = normalize_text(text)
    matches: list[str] = []
    for label, terms in rules.items():
        hits = sum(1 for term in terms if normalize_text(term) in normalized)
        if hits >= 1:
            matches.append(label)
    return matches


def extract_hidden_requirements(jd_text: str) -> list[str]:
    return _match_rules(jd_text, HIDDEN_REQUIREMENT_RULES)


def extract_behavioral_traits(jd_text: str) -> list[str]:
    return _match_rules(jd_text, BEHAVIORAL_RULES)


def extract_disqualifiers(jd_text: str) -> list[str]:
    return _match_rules(jd_text, DISQUALIFIER_RULES)


def extract_jd_intelligence(jd_text: str) -> dict[str, Any]:
    parsed = parse_jd(jd_text)
    matches = find_ontology_matches(jd_text)
    domains = unique_preserve_order(match["domain"] for match in matches if match["domain"] != "unknown")
    intelligence = {
        "must_have_skills": parsed["must_have"],
        "nice_to_have_skills": parsed["nice_to_have"],
        "all_detected_skills": extract_skills(jd_text),
        "domains": domains,
        "career_preferences": _match_rules(jd_text, CAREER_PREFERENCE_RULES),
        "behavioral_traits": extract_behavioral_traits(jd_text),
        "disqualifiers": extract_disqualifiers(jd_text),
        "hidden_requirements": extract_hidden_requirements(jd_text),
        "experience": parsed["experience"],
        "seniority": parsed["seniority"],
        "primary_domain": parsed["domain"],
    }
    logger.debug("JD intelligence: %s", intelligence)
    return intelligence

