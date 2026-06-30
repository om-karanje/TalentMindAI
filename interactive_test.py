from __future__ import annotations

from src.candidate_text import candidate_to_text
from src.data_loader import load_candidates, load_job_description
from src.semantic_matcher import rank_candidates
from src.utils import OUTPUT_DIR, dump_json, setup_logging, write_csv


def main() -> None:
    setup_logging(False)
    jd_path = input("JD path (blank for data/job_description.*): ").strip() or None
    candidates_path = input("Candidate dataset path (blank for data/candidates.*): ").strip() or None
    top_k_raw = input("Top K to display/save (blank for all candidates): ").strip()
    top_k = int(top_k_raw) if top_k_raw else None

    jd_text = load_job_description(jd_path)
    candidates = load_candidates(candidates_path)
    ranked = rank_candidates(jd_text, candidates, top_k=top_k)

    print("\nRanked candidates")
    print("Rank | Candidate ID | Semantic Score")
    print("-" * 42)
    for item in ranked:
        print(f"{item['rank']:>4} | {item['candidate_id']:<12} | {item['semantic_score']:>6.2f}")

    write_csv(
        OUTPUT_DIR / "top_candidates.csv",
        [
            {
                "rank": item["rank"],
                "candidate_id": item["candidate_id"],
                "semantic_score": item["semantic_score"],
            }
            for item in ranked
        ],
        ["rank", "candidate_id", "semantic_score"],
    )
    write_csv(
        OUTPUT_DIR / "all_candidates_ranked.csv",
        [
            {
                "rank": item["rank"],
                "candidate_id": item["candidate_id"],
                "semantic_score": item["semantic_score"],
            }
            for item in ranked
        ],
        ["rank", "candidate_id", "semantic_score"],
    )
    dump_json(
        OUTPUT_DIR / "candidate_explanations.json",
        [
            {
                "candidate_id": item["candidate_id"],
                "semantic_score": item["semantic_score"],
                "matched_domains": item["matched_domains"],
                "matched_skills": item["matched_skills"],
                "reasons": item["reason_for_match"],
            }
            for item in ranked
        ],
    )
    candidate_by_id = {candidate.get("candidate_id", ""): candidate for candidate in candidates}
    dump_json(
        OUTPUT_DIR / "semantic_features.json",
        [
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
        ],
    )
    print(f"\nSaved outputs under {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
