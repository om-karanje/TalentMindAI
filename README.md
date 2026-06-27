# TalentMindAI - Person 2 Semantic Matching

This module implements the Person 2 scope for the Redrob Intelligent Candidate Discovery & Ranking Challenge:

- JD understanding
- JD intelligence
- Skill ontology
- Candidate text generation
- Candidate intelligence
- Semantic candidate-job matching

It does not train or fine-tune any model. It uses pretrained CPU-friendly embeddings from `BAAI/bge-small-en-v1.5`.

## Installation

```bash
cd project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

The first run downloads the embedding model through `sentence-transformers`.

## Data Placement

Place one job description file in `project/data/`:

- `job_description.txt`
- `job_description.md`
- `job_description.pdf`

Place one candidate dataset in `project/data/`:

- `candidates.json`
- `candidates.jsonl`
- `candidates_part2.json`
- any other `candidates*.json` or `candidates*.jsonl` file

`candidates.json` may be a single candidate object, a list of candidate objects, or an object shaped like:

```json
{
  "candidates": []
}
```

## Run Matching

```bash
python run_matching.py
```

With explicit paths:

```bash
python run_matching.py --jd data/job_description.txt --candidates data/candidates.jsonl
```

Debug mode:

```bash
python run_matching.py --debug
```

By default, the pipeline ranks and saves every candidate found in `data/candidates*.json` and `data/candidates*.jsonl`. Use `--top-k 20` only when you intentionally want a limited output.

Outputs:

- `outputs/top_candidates.csv`
- `outputs/all_candidates_ranked.csv`
- `outputs/candidate_explanations.json`
- `outputs/semantic_features.json`
- `outputs/parsed_jd.json`
- `outputs/jd_intelligence.json`

`top_candidates.csv` and `all_candidates_ranked.csv` both contain the full ordered ranking unless `--top-k` is provided:

```text
rank,candidate_id,semantic_score
```

## Interactive Test

```bash
python interactive_test.py
```

The prompt accepts custom JD and candidate paths, displays the top candidates, and saves the same output files.
Leave the Top K prompt blank to rank and save every candidate.

## Notebook

Open:

```text
notebooks/semantic_testing.ipynb
```

The notebook workflow:

1. Load JD
2. Load candidates
3. Parse JD
4. Generate JD intelligence
5. Generate candidate intelligence
6. Create embeddings
7. Rank candidates
8. Inspect explanations

## Stable APIs

Person 3 and Person 4 should import from `src.interfaces`:

```python
from src.interfaces import (
    parse_jd,
    extract_jd_intelligence,
    candidate_to_text,
    extract_candidate_intelligence,
    semantic_similarity,
    rank_candidates,
)
```

### `parse_jd(jd_text)`

Returns:

```python
{
    "must_have": [],
    "nice_to_have": [],
    "experience": 0,
    "seniority": "",
    "domain": "",
}
```

### `extract_jd_intelligence(jd_text)`

Returns intent-level fields:

```python
{
    "must_have_skills": [],
    "nice_to_have_skills": [],
    "domains": [],
    "career_preferences": [],
    "behavioral_traits": [],
    "disqualifiers": [],
    "hidden_requirements": [],
}
```

### `candidate_to_text(candidate_json)`

Builds a rich semantic text block from profile, headline, summary, current title, skills, career history, and education.

### `extract_candidate_intelligence(candidate_json)`

Returns:

```python
{
    "technical_domains": [],
    "skill_categories": [],
    "career_patterns": [],
    "experience_years": 0,
    "leadership_indicators": [],
    "retrieval_experience": False,
    "ranking_experience": False,
    "recommendation_experience": False,
    "product_company_experience": False,
    "startup_experience": False,
    "career_summary": "",
}
```

### `semantic_similarity(left_text, right_text)`

Returns a `0-100` cosine similarity score using pretrained embeddings.

### `rank_candidates(jd_text, candidates, top_k=None)`

Returns ranked dictionaries:

```python
{
    "rank": 1,
    "candidate_id": "CAND_0000001",
    "semantic_score": 91.2,
    "embedding_score": 86.7,
    "matched_skills": [],
    "matched_domains": [],
    "experience": 6.5,
    "candidate_intelligence": {},
    "reason_for_match": []
}
```

## Integration Guide

Person 1 should provide cleaned candidate objects or `candidate_features`. This module can consume raw candidate JSON directly and can also be called after Person 1 normalization.

Person 2 outputs:

- `parsed_jd`
- `jd_intelligence`
- `candidate_text`
- `candidate_intelligence`
- `semantic_score`
- `matched_skills`
- `matched_domains`
- `reason_for_match`

The main handoff file is `outputs/semantic_features.json`. It contains each candidate's rank, semantic score, embedding score, matched skills/domains, candidate intelligence, candidate text, and reasons.

Person 3 should combine these semantic outputs with behavioral, availability, trust, and honeypot signals.

Person 4 should use `semantic_score`, `candidate_intelligence`, `matched_domains`, and `reason_for_match` for final ranking and explainability.

## Design Notes

This system avoids pure keyword counting. It uses:

- Ontology normalization for skills and adjacent capabilities
- Candidate evidence extraction from career history and profile text
- Pretrained semantic embeddings for JD-candidate similarity
- Lightweight evidence bonuses and risk penalties for explainable scoring

The scoring layer is intentionally transparent so the final ranking owner can tune weights without retraining a model.
