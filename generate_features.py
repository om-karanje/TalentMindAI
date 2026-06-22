"""
Reads:candidates.jsonl
Uses:behavior_engine.py, trust_engine.py
Creates:candidate_features.csv
"""

import json
import pandas as pd

from behavior_engine import generate_behavior_features
from trust_engine import generate_trust_features

INPUT_FILE = "candidates.jsonl"
OUTPUT_FILE = "candidate_features.csv"

def process_candidates():
    results = []
    count = 0

    with open(INPUT_FILE,"r",encoding="utf-8") as f:
        for line in f:
            candidate = json.loads(line)

            behavior_features = (generate_behavior_features(candidate))
            trust_features = (generate_trust_features(candidate))

            final_features = {
                "candidate_id":candidate.get("candidate_id"),
                "behavior_score":behavior_features["behavior_score"],
                "availability_score":behavior_features["availability_score"],
                "market_interest_score":behavior_features["market_interest_score"],
                "trust_score":trust_features["trust_score"],
                "honeypot_penalty":trust_features["honeypot_penalty"],
                "trust_flags":", ".join(trust_features["trust_flags"])
            }

            results.append(final_features)
            count += 1

            if count % 5000 == 0:
                print(f"Processed {count} candidates...")

    return results

def print_statistics(df):
    print("\n========== FEATURE STATS ==========")

    columns = [
        "behavior_score",
        "availability_score",
        "market_interest_score",
        "trust_score",
        "honeypot_penalty"
    ]

    for col in columns:
        print(f"\n{col}")
        print("Min:",round(df[col].min(),4))
        print("Max:",round(df[col].max(),4))
        print("Avg:",round(df[col].mean(),4))

def main():
    print("\nStarting feature generation...")

    results = process_candidates()
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE,index=False)

    print(f"\nSaved file: {OUTPUT_FILE}")
    print(f"Total candidates: {len(df)}")
    print_statistics(df)
    print("\nFeature generation complete.")

if __name__ == "__main__":
    main()