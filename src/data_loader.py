from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .utils import DATA_DIR, as_list

logger = logging.getLogger(__name__)


class DataLoadError(RuntimeError):
    """Raised when challenge input files cannot be found or parsed."""


def load_json(path: str | Path) -> Any:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise DataLoadError(f"JSON file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise DataLoadError(f"Invalid JSON in {file_path}: {exc}") from exc


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    rows: list[dict[str, Any]] = []
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                clean = line.strip()
                if not clean:
                    continue
                try:
                    value = json.loads(clean)
                except json.JSONDecodeError as exc:
                    raise DataLoadError(
                        f"Invalid JSONL at {file_path}:{line_number}: {exc}"
                    ) from exc
                if not isinstance(value, dict):
                    raise DataLoadError(
                        f"JSONL row {line_number} in {file_path} is not an object."
                    )
                rows.append(value)
    except FileNotFoundError as exc:
        raise DataLoadError(f"JSONL file not found: {file_path}") from exc
    return rows


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise DataLoadError(
            "PDF loading requires pypdf. Install requirements.txt or provide a .txt/.md JD."
        ) from exc

    try:
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
    except Exception as exc:
        raise DataLoadError(f"Could not read PDF job description at {path}: {exc}") from exc
    text = "\n".join(pages).strip()
    if not text:
        raise DataLoadError(f"No extractable text found in PDF: {path}")
    return text


def _find_first(base_dir: Path, names: list[str]) -> Path:
    matches = [base_dir / name for name in names if (base_dir / name).exists()]
    if not matches:
        raise DataLoadError(
            f"Expected one of {', '.join(names)} in {base_dir.resolve()}."
        )
    if len(matches) > 1:
        logger.warning("Multiple input files found; using %s", matches[0])
    return matches[0]


def _find_candidate_files(base_dir: Path) -> list[Path]:
    exact = [base_dir / name for name in ("candidates.json", "candidates.jsonl") if (base_dir / name).exists()]
    patterned = sorted(
        path
        for path in base_dir.glob("candidates*")
        if path.is_file() and path.suffix.lower() in {".json", ".jsonl"} and path not in exact
    )
    files = exact + patterned
    if not files:
        raise DataLoadError(
            f"Expected candidates.json, candidates.jsonl, or candidates*.json/jsonl in {base_dir.resolve()}."
        )
    return files


def load_job_description(path: str | Path | None = None) -> str:
    jd_path = Path(path) if path else _find_first(
        DATA_DIR,
        ["job_description.txt", "job_description.md", "job_description.pdf"],
    )
    suffix = jd_path.suffix.lower()
    logger.info("Loading job description from %s", jd_path)
    if suffix in {".txt", ".md"}:
        try:
            text = jd_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:
            raise DataLoadError(f"Job description not found: {jd_path}") from exc
        if not text:
            raise DataLoadError(f"Job description is empty: {jd_path}")
        return text
    if suffix == ".pdf":
        return _read_pdf(jd_path)
    raise DataLoadError("Job description must be .txt, .md, or .pdf.")


def _load_candidate_file(candidate_path: Path) -> list[dict[str, Any]]:
    suffix = candidate_path.suffix.lower()
    if suffix == ".jsonl":
        candidates = load_jsonl(candidate_path)
    elif suffix == ".json":
        raw = load_json(candidate_path)
        if isinstance(raw, dict) and isinstance(raw.get("candidates"), list):
            candidates = raw["candidates"]
        elif isinstance(raw, list):
            candidates = raw
        elif isinstance(raw, dict):
            candidates = [raw]
        else:
            raise DataLoadError(
                "Candidate JSON must be an object, a list, or {'candidates': [...]}"
            )
    else:
        raise DataLoadError("Candidate dataset must be .json or .jsonl.")

    normalized = [candidate for candidate in as_list(candidates) if isinstance(candidate, dict)]
    if not normalized:
        raise DataLoadError(f"No candidate objects found in {candidate_path}")
    return normalized


def load_candidates(path: str | Path | None = None) -> list[dict[str, Any]]:
    candidate_paths = [Path(path)] if path else _find_candidate_files(DATA_DIR)
    all_candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for candidate_path in candidate_paths:
        logger.info("Loading candidates from %s", candidate_path)
        for candidate in _load_candidate_file(candidate_path):
            candidate_id = str(candidate.get("candidate_id", "")).strip()
            if candidate_id and candidate_id in seen_ids:
                logger.warning("Skipping duplicate candidate_id=%s from %s", candidate_id, candidate_path)
                continue
            if candidate_id:
                seen_ids.add(candidate_id)
            all_candidates.append(candidate)

    if not all_candidates:
        raise DataLoadError("No candidate objects found in candidate input files.")
    logger.info("Loaded %d total candidates from %d file(s)", len(all_candidates), len(candidate_paths))
    return all_candidates
