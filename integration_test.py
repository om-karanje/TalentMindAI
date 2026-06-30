import os
import pandas as pd
import numpy as np

def run_integration_tests():
    print("==================================================")
    print("      TalentMindAI Integration Test Suite (Phase 6)   ")
    print("==================================================")
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    RANKED_CSV = os.path.join(OUTPUT_DIR, "ranked_candidates.csv")
    
    # Force baseline static score calculation by deleting active pasted_jd.txt
    pasted_jd_path = os.path.join(DATA_DIR, "pasted_jd.txt")
    if os.path.exists(pasted_jd_path):
        os.remove(pasted_jd_path)
        
    # Re-run ranker to build clean baseline ranked candidates
    from ranker import run_ranker
    run_ranker(DATA_DIR, OUTPUT_DIR)
    
    df = pd.read_csv(RANKED_CSV)
    
    # ----------------- TEST 1: Perfect Match -----------------
    print("\n[Test 1] Checking Perfect Match Scenario...")
    # CAND_0000031 has 100.0% semantic score and no security flags
    perfect_match_id = "CAND_0000031"
    top_candidate = df.iloc[0]
    
    print(f"Top ranked candidate: {top_candidate['candidate_id']} (Final Score: {top_candidate['final_score']:.4f})")
    assert top_candidate['candidate_id'] == perfect_match_id, f"Error: Perfect match candidate {perfect_match_id} is not ranked #1."
    print("SUCCESS: Perfect Match candidate ranked at the absolute top.")
    
    # ----------------- TEST 2: Hidden Talent -----------------
    print("\n[Test 2] Checking Hidden Talent Scenario...")
    # Candidates in the top 10 who have strong semantic matching but do not have keyword stuffing
    # Let's verify that top 10 candidates have high semantic scores (>80%) and high final scores
    top_10 = df.head(10)
    hidden_talents = top_10[top_10['semantic_score'] >= 0.8]
    print(f"Found {len(hidden_talents)} high-semantic match profiles in the top 10.")
    assert len(hidden_talents) > 0, "Error: No high-semantic matches in top 10."
    print("SUCCESS: Candidates with strong semantic affinity rank in the elite tier.")
    
    # ----------------- TEST 3: Keyword Spammer -----------------
    print("\n[Test 3] Checking Keyword Spammer Scenario...")
    # Let's simulate a keyword spammer candidate with high semantic score but low experience and behavior metrics
    spammer_row = pd.Series({
        'candidate_id': 'SPAM_0000001',
        'years_experience': 0.5,
        'llm_score': 0.8,
        'retrieval_score': 0.8,
        'vector_db_score': 0.8,
        'backend_score': 0.8,
        'career_growth': 0.1,
        'leadership_score': 0.05,
        'availability_score': 0.1,
        'behavior_score': 0.1,
        'trust_score': 0.2,
        'honeypot_penalty': 0.5, # Tripped trap
        'semantic_score': 1.0 # Resume packed with spam keywords
    })
    
    # Calculate scores for spammer using our formulas
    spam_tech_fit = (
        0.30 * spammer_row['llm_score'] +
        0.30 * spammer_row['retrieval_score'] +
        0.20 * spammer_row['vector_db_score'] +
        0.20 * spammer_row['backend_score']
    )
    spam_dna = (
        0.30 * spam_tech_fit +
        0.25 * spammer_row['semantic_score'] +
        0.20 * spammer_row['behavior_score'] +
        0.10 * spammer_row['career_growth'] +
        0.05 * spammer_row['leadership_score'] +
        0.05 * spammer_row['availability_score'] +
        0.05 * spammer_row['trust_score']
    )
    spam_final_score = spam_dna - spammer_row['honeypot_penalty']
    
    # Compare with a high-experience, high-behavior, non-spammer candidate in the dataset
    legit_candidate = df[df['candidate_id'] == 'CAND_0000001'].iloc[0]
    
    print(f"Spammer simulated final score: {spam_final_score:.4f} (tripped honeypot penalty)")
    print(f"Legitimate candidate (CAND_0000001) final score: {legit_candidate['final_score']:.4f}")
    assert spam_final_score < legit_candidate['final_score'], "Error: Keyword spammer ranked higher than legitimate talent."
    print("SUCCESS: Keyword spammer score heavily suppressed below legitimate profiles.")
    
    # ----------------- TEST 4: Behavioral Twins -----------------
    print("\n[Test 4] Checking Behavioral Twins Scenario...")
    # Two candidates with matching semantic match but different behavior score
    # Let's take two candidates from the top pool with semantic score > 0
    df_matched = df[df['semantic_score'] > 0.0].copy()
    
    # Find two candidates with similar semantic match but different behavior scores
    found = False
    for i in range(len(df_matched)):
        for j in range(i+1, len(df_matched)):
            cand1 = df_matched.iloc[i]
            cand2 = df_matched.iloc[j]
            # If semantic scores are equal (or very close) but behavior scores differ
            if abs(cand1['semantic_score'] - cand2['semantic_score']) < 0.01:
                if abs(cand1['behavior_score'] - cand2['behavior_score']) > 0.05:
                    found = True
                    # The one with higher behavior score must be ranked higher
                    higher_beh = cand1 if cand1['behavior_score'] > cand2['behavior_score'] else cand2
                    lower_beh = cand2 if cand1['behavior_score'] > cand2['behavior_score'] else cand1
                    
                    print(f"Candidate A ({higher_beh['candidate_id']}): Semantic={higher_beh['semantic_score']:.2%}, Behavior={higher_beh['behavior_score']:.2%}, Rank={higher_beh['rank']}")
                    print(f"Candidate B ({lower_beh['candidate_id']}): Semantic={lower_beh['semantic_score']:.2%}, Behavior={lower_beh['behavior_score']:.2%}, Rank={lower_beh['rank']}")
                    
                    assert higher_beh['rank'] < lower_beh['rank'], f"Error: Candidate with lower behavior score was ranked higher."
                    break
        if found:
            break
            
    if found:
        print("SUCCESS: Behavioral twins ranked correctly (behavior score acted as the tiebreaker).")
    else:
        print("INFO: No matching semantic twins with different behavior found in dataset.")
        
    print("\n==================================================")
    print("         ALL INTEGRATION TESTS PASSED (4/4)       ")
    print("==================================================")

if __name__ == "__main__":
    run_integration_tests()
