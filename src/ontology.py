from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from .utils import DATA_DIR, normalize_text

logger = logging.getLogger(__name__)
DEFAULT_ONTOLOGY_PATH = DATA_DIR / "skill_ontology.json"


class OntologyError(RuntimeError):
    """Raised when the skill ontology is missing or malformed."""


@lru_cache(maxsize=4)
def load_ontology(path: str | Path = DEFAULT_ONTOLOGY_PATH) -> dict[str, Any]:
    ontology_path = Path(path)
    try:
        data = json.loads(ontology_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OntologyError(f"Skill ontology not found: {ontology_path}") from exc
    except json.JSONDecodeError as exc:
        raise OntologyError(f"Invalid ontology JSON at {ontology_path}: {exc}") from exc
    if not isinstance(data, dict) or "term_mappings" not in data:
        raise OntologyError("Ontology must contain a 'term_mappings' object.")
    return data


def normalize_skill(skill: str) -> str:
    return normalize_text(skill)


def map_skill(skill: str, ontology: dict[str, Any] | None = None) -> dict[str, str]:
    active = ontology or load_ontology()
    normalized = normalize_skill(skill)
    term_mappings: dict[str, Any] = active.get("term_mappings", {})
    for term, value in term_mappings.items():
        clean_term = normalize_text(term)
        if clean_term and (normalized == clean_term or clean_term in normalized):
            return {
                "input": skill,
                "normalized": normalized,
                "canonical": value.get("canonical", clean_term),
                "category": value.get("category", "unknown"),
                "domain": value.get("domain", "unknown"),
            }

    return {
        "input": skill,
        "normalized": normalized,
        "canonical": normalized,
        "category": "unknown",
        "domain": "unknown",
    }


def find_ontology_matches(text: str, ontology: dict[str, Any] | None = None) -> list[dict[str, str]]:
    active = ontology or load_ontology()
    normalized_text = f" {normalize_text(text)} "
    matches: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for term, value in active.get("term_mappings", {}).items():
        clean_term = normalize_text(term)
        if not clean_term:
            continue
        if f" {clean_term} " in normalized_text or clean_term in normalized_text:
            key = (value.get("canonical", clean_term), value.get("category", "unknown"))
            if key in seen:
                continue
            seen.add(key)
            matches.append(
                {
                    "term": term,
                    "canonical": value.get("canonical", clean_term),
                    "category": value.get("category", "unknown"),
                    "domain": value.get("domain", "unknown"),
                }
            )
    return matches
