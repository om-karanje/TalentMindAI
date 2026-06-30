from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Iterable, Sequence

from .candidate_intelligence import extract_candidate_intelligence
from .candidate_text import candidate_to_text
from .jd_intelligence import extract_jd_intelligence
from .ontology import find_ontology_matches
from .utils import cosine_similarity_vector, normalize_text, score_from_cosine, unique_preserve_order

logger = logging.getLogger(__name__)
MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def load_model(model_name: str = MODEL_NAME) -> Any:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is required for semantic matching. "
            "Install project/requirements.txt first."
        ) from exc
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name, device="cpu")


def _embedding_text(text: str, purpose: str) -> str:
    clean = text.strip()
    if purpose == "query":
        return f"Represent this job description for finding semantically matching candidates: {clean}"
    return f"Represent this candidate profile for matching to a job description: {clean}"


def get_embedding(text: str, model: Any | None = None, purpose: str = "document") -> list[float]:
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text.")
    active_model = model or load_model()
    vector = active_model.encode(_embedding_text(text, purpose), normalize_embeddings=True)
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return list(vector)


def semantic_similarity(left_text: str, right_text: str, model: Any | None = None) -> float:
    active_model = model or load_model()
    left_embedding = get_embedding(left_text, active_model, purpose="query")
    right_embedding = get_embedding(right_text, active_model, purpose="document")
    return score_from_cosine(cosine_similarity_vector(left_embedding, right_embedding))


def _matched_skills(jd_intelligence: dict[str, Any], candidate_text: str) -> list[str]:
    candidate_matches = find_ontology_matches(candidate_text)
    candidate_canonicals = {match["canonical"] for match in candidate_matches}
    jd_skills = set(jd_intelligence.get("must_have_skills", [])) | set(
        jd_intelligence.get("nice_to_have_skills", [])
    )
    return unique_preserve_order(skill for skill in jd_skills if skill in candidate_canonicals)


def _matched_domains(jd_intelligence: dict[str, Any], candidate_intelligence: dict[str, Any]) -> list[str]:
    jd_domains = set(jd_intelligence.get("domains", []))
    candidate_domains = set(candidate_intelligence.get("technical_domains", []))
    return unique_preserve_order(domain for domain in jd_domains.intersection(candidate_domains))


def _evidence_bonus(jd_intelligence: dict[str, Any], candidate_intelligence: dict[str, Any]) -> float:
    hidden = set(jd_intelligence.get("hidden_requirements", []))
    bonus = 0.0
    if "ranking_or_retrieval_ownership" in hidden:
        if candidate_intelligence.get("retrieval_experience"):
            bonus += 5.0
        if candidate_intelligence.get("ranking_experience"):
            bonus += 5.0
        if candidate_intelligence.get("recommendation_experience"):
            bonus += 4.0
    if "product_judgment" in hidden and candidate_intelligence.get("product_company_experience"):
        bonus += 3.0
    if "startup_adaptability" in hidden and candidate_intelligence.get("startup_experience"):
        bonus += 2.0
    if candidate_intelligence.get("leadership_indicators"):
        bonus += 2.0
    return bonus


def _risk_penalty(jd_intelligence: dict[str, Any], candidate_intelligence: dict[str, Any]) -> float:
    penalty = 0.0
    categories = set(candidate_intelligence.get("skill_categories", []))
    has_claimed_ai = bool(categories.intersection({"llm", "rag", "retrieval", "vector_database"}))
    has_evidence = any(
        candidate_intelligence.get(key)
        for key in ("retrieval_experience", "ranking_experience", "recommendation_experience")
    )
    if has_claimed_ai and not has_evidence:
        penalty += 6.0
    if "services_or_consulting_exposure" in candidate_intelligence.get("career_patterns", []):
        penalty += 2.0
    required_years = float(jd_intelligence.get("experience") or 0)
    if required_years and candidate_intelligence.get("experience_years", 0) < required_years:
        penalty += 4.0
    return penalty


def _reason_for_match(
    jd_intelligence: dict[str, Any],
    candidate_intelligence: dict[str, Any],
    matched_domains: list[str],
    matched_skills: list[str],
) -> list[str]:
    reasons: list[str] = []
    if matched_domains:
        reasons.append(f"Matches JD domains: {', '.join(matched_domains)}")
    if matched_skills:
        reasons.append(f"Matches relevant skills: {', '.join(matched_skills[:8])}")
    if candidate_intelligence.get("retrieval_experience"):
        reasons.append("Shows retrieval or search experience")
    if candidate_intelligence.get("ranking_experience"):
        reasons.append("Shows ranking or ranking-evaluation experience")
    if candidate_intelligence.get("recommendation_experience"):
        reasons.append("Shows recommendation or personalization experience")
    if candidate_intelligence.get("product_company_experience"):
        reasons.append("Career history indicates product or platform relevance")
    if not reasons:
        reasons.append("Embedding similarity found broad semantic overlap, but limited explicit evidence")
    return reasons


def _score_candidate(
    jd_text: str,
    jd_embedding: Sequence[float],
    jd_intelligence: dict[str, Any],
    candidate: dict[str, Any],
    model: Any,
) -> dict[str, Any]:
    text = candidate_to_text(candidate)
    candidate_embedding = get_embedding(text, model, purpose="document")
    base_score = score_from_cosine(cosine_similarity_vector(jd_embedding, candidate_embedding))
    candidate_intelligence = extract_candidate_intelligence(candidate)
    matched_skills = _matched_skills(jd_intelligence, text)
    matched_domains = _matched_domains(jd_intelligence, candidate_intelligence)
    adjusted_score = base_score + _evidence_bonus(jd_intelligence, candidate_intelligence)
    adjusted_score -= _risk_penalty(jd_intelligence, candidate_intelligence)
    final_score = round(max(0.0, min(100.0, adjusted_score)), 2)
    return {
        "candidate_id": candidate.get("candidate_id", ""),
        "semantic_score": final_score,
        "embedding_score": base_score,
        "matched_skills": matched_skills,
        "matched_domains": matched_domains,
        "experience": candidate_intelligence.get("experience_years", 0),
        "candidate_intelligence": candidate_intelligence,
        "reason_for_match": _reason_for_match(
            jd_intelligence, candidate_intelligence, matched_domains, matched_skills
        ),
    }


def rank_candidates(
    jd_text: str,
    candidates: Iterable[dict[str, Any]],
    top_k: int | None = None,
    model: Any | None = None,
) -> list[dict[str, Any]]:
    if not jd_text or not jd_text.strip():
        raise ValueError("JD text cannot be empty.")
    candidate_list = list(candidates)
    if not candidate_list:
        return []
    active_model = model or load_model()
    jd_intelligence = extract_jd_intelligence(jd_text)
    jd_embedding = get_embedding(jd_text, active_model, purpose="query")
    results = [
        _score_candidate(jd_text, jd_embedding, jd_intelligence, candidate, active_model)
        for candidate in candidate_list
    ]
    ranked = sorted(results, key=lambda item: item["semantic_score"], reverse=True)
    for index, item in enumerate(ranked, start=1):
        item["rank"] = index
    return ranked[:top_k] if top_k else ranked

