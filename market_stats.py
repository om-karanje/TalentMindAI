"""
market_stats.py

Scans entire candidates.jsonl dataset
and finds maximum values for:

1. profile_views_received_30d
2. saved_by_recruiters_30d
3. search_appearance_30d

Use output values inside behavior_engine.py
"""

import json

INPUT_FILE = "candidates.jsonl"


def main():

    max_profile_views = 0
    max_recruiter_saves = 0
    max_search_appearance = 0

    candidate_count = 0

    print("Scanning dataset...\n")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            candidate = json.loads(line)

            signals = candidate.get(
                "redrob_signals",
                {}
            )

            profile_views = signals.get(
                "profile_views_received_30d",
                0
            )

            recruiter_saves = signals.get(
                "saved_by_recruiters_30d",
                0
            )

            search_appearance = signals.get(
                "search_appearance_30d",
                0
            )

            max_profile_views = max(
                max_profile_views,
                profile_views
            )

            max_recruiter_saves = max(
                max_recruiter_saves,
                recruiter_saves
            )

            max_search_appearance = max(
                max_search_appearance,
                search_appearance
            )

            candidate_count += 1

            if candidate_count % 10000 == 0:

                print(
                    f"Scanned {candidate_count} candidates..."
                )

    print("\n========== RESULTS ==========\n")

    print(
        "MAX_PROFILE_VIEWS =",
        max_profile_views
    )

    print(
        "MAX_RECRUITER_SAVES =",
        max_recruiter_saves
    )

    print(
        "MAX_SEARCH_APPEARANCE =",
        max_search_appearance
    )

    print(
        "\nTotal Candidates Scanned =",
        candidate_count
    )


if __name__ == "__main__":
    main()