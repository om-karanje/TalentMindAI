from __future__ import annotations

import argparse
import logging

from src.data_loader import load_candidates, load_job_description
from src.candidate_text import candidate_to_text
from src.jd_intelligence import extract_jd_intelligence
from src.jd_parser import parse_jd
from src.semantic_matcher import rank_candidates
from src.utils import OUTPUT_DIR, dump_json, setup_logging, write_csv

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run TalentMindAI Person 2 semantic matching.")
    parser.add_argument("--jd", type=str, default=None, help="Optional path to job_description txt/md/pdf.")
    parser.add_argument("--candidates", type=str, default=None, help="Optional path to candidates json/jsonl.")
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Optional display/output limit. By default every candidate is ranked and saved.",
    )
    parser.add_argument("--debug", action="store_true", help="Print detailed candidate debug output.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    setup_logging(args.debug)

    jd_text = load_job_description(args.jd)
    candidates = load_candidates(args.candidates)
    parsed_jd = parse_jd(jd_text)
    jd_intelligence = extract_jd_intelligence(jd_text)

    logger.info("Loaded %d candidates", len(candidates))
    logger.info("Parsed JD seniority=%s domain=%s", parsed_jd["seniority"], parsed_jd["domain"])
    ranked = rank_candidates(jd_text, candidates, top_k=args.top_k)

    top_rows = [
        {
            "rank": item["rank"],
            "candidate_id": item["candidate_id"],
            "semantic_score": item["semantic_score"],
        }
        for item in ranked
    ]
    write_csv(OUTPUT_DIR / "top_candidates.csv", top_rows, ["rank", "candidate_id", "semantic_score"])
    write_csv(OUTPUT_DIR / "all_candidates_ranked.csv", top_rows, ["rank", "candidate_id", "semantic_score"])

    explanations = [
        {
            "candidate_id": item["candidate_id"],
            "semantic_score": item["semantic_score"],
            "matched_domains": item["matched_domains"],
            "matched_skills": item["matched_skills"],
            "reasons": item["reason_for_match"],
        }
        for item in ranked
    ]
    dump_json(OUTPUT_DIR / "candidate_explanations.json", explanations)
    candidate_by_id = {candidate.get("candidate_id", ""): candidate for candidate in candidates}
    semantic_features = [
        {
            "candidate_id": item["candidate_id"],
            "rank": item["rank"],
            "semantic_score": item["semantic_score"],
            "embedding_score": item["embedding_score"],
            "matched_domains": item["matched_domains"],
            "matched_skills": item["matched_skills"],
            "candidate_intelligence": item["candidate_intelligence"],
            "candidate_text": candidate_to_text(candidate_by_id.get(item["candidate_id"], {})),
            "reason_for_match": item["reason_for_match"],
        }
        for item in ranked
    ]
    dump_json(OUTPUT_DIR / "semantic_features.json", semantic_features)
    dump_json(OUTPUT_DIR / "parsed_jd.json", parsed_jd)
    dump_json(OUTPUT_DIR / "jd_intelligence.json", jd_intelligence)

    if args.debug:
        for item in ranked:
            print(
                "\n".join(
                    [
                        f"Candidate ID: {item['candidate_id']}",
                        f"Semantic Score: {item['semantic_score']}",
                        f"Matched Skills: {', '.join(item['matched_skills']) or 'None'}",
                        f"Matched Domains: {', '.join(item['matched_domains']) or 'None'}",
                        f"Experience: {item['experience']}",
                        f"Reason For Match: {'; '.join(item['reason_for_match'])}",
                        "",
                    ]
                )
            )

    logger.info("Saved %s", OUTPUT_DIR / "top_candidates.csv")
    logger.info("Saved %s", OUTPUT_DIR / "all_candidates_ranked.csv")
    logger.info("Saved %s", OUTPUT_DIR / "candidate_explanations.json")
    logger.info("Saved %s", OUTPUT_DIR / "semantic_features.json")


if __name__ == "__main__":
    main()
