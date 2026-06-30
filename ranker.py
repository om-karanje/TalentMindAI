import os
import json
import pandas as pd
import numpy as np

# Global paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define skill categories for feature engineering
LLM_SKILLS = {
    "large language models", "transformer models", "model fine tuning",
    "parameter efficient fine tuning", "sentence transformers", "natural language processing"
}

RETRIEVAL_SKILLS = {
    "information retrieval", "matching systems", "search systems",
    "search infrastructure", "ranking systems", "embeddings",
    "text embeddings", "embedding models", "ai evaluation", "ranking evaluation"
}

VECTOR_DB_SKILLS = {
    "vector databases", "vector indexes", "embedding operations"
}

BACKEND_SKILLS = {
    "python", "distributed systems", "go"
}

def engineer_features(raw_features_path, explanations_json_path, parquet_output_path):
    """
    Person 1 Mock/Feature Engineering Module.
    Loads raw candidate features and uses explanations (matched skills) to engineer:
    llm_score, retrieval_score, vector_db_score, backend_score, career_growth, and leadership_score.
    Saves the output to parquet format.
    """
    print("Starting Feature Engineering Engine...")
    
    # Load raw features
    df = pd.read_csv(raw_features_path)
    
    # Load explanation metadata for skill matching (maps candidate_id -> matched_skills)
    with open(explanations_json_path, 'r', encoding='utf-8') as f:
        explanations = json.load(f)
        
    skills_map = {item['candidate_id']: set(item['matched_skills']) for item in explanations}
    
    # Initialize technical score columns with baseline default values
    llm_scores = []
    retrieval_scores = []
    vector_db_scores = []
    backend_scores = []
    leadership_scores = []
    
    for idx, row in df.iterrows():
        cand_id = row['candidate_id']
        matched = skills_map.get(cand_id, set())
        
        # 1. LLM Score (0-1 scale)
        if len(matched & LLM_SKILLS) > 0:
            llm_val = min(1.0, 0.2 + 0.2 * len(matched & LLM_SKILLS))
        else:
            # Baseline for candidates not in top 50, derived from skills count
            llm_val = min(0.4, 0.02 * row['skills_count'])
        llm_scores.append(llm_val)
        
        # 2. Retrieval Score (0-1 scale)
        if len(matched & RETRIEVAL_SKILLS) > 0:
            retrieval_val = min(1.0, 0.2 + 0.15 * len(matched & RETRIEVAL_SKILLS))
        else:
            retrieval_val = min(0.4, 0.015 * row['skills_count'])
        retrieval_scores.append(retrieval_val)
        
        # 3. Vector DB Score (0-1 scale)
        if len(matched & VECTOR_DB_SKILLS) > 0:
            vector_db_val = min(1.0, 0.3 + 0.3 * len(matched & VECTOR_DB_SKILLS))
        else:
            vector_db_val = min(0.3, 0.01 * row['skills_count'])
        vector_db_scores.append(vector_db_val)
        
        # 4. Backend Score (0-1 scale)
        if len(matched & BACKEND_SKILLS) > 0:
            backend_val = min(1.0, 0.3 + 0.3 * len(matched & BACKEND_SKILLS))
        else:
            backend_val = min(0.5, 0.025 * row['skills_count'])
        backend_scores.append(backend_val)
        
        # 5. Leadership Score (0-1 scale)
        years_exp = row['years_experience']
        if years_exp > 8.0:
            lead_val = min(1.0, 0.4 + 0.05 * (years_exp - 8.0) + 0.05 * row['career_count'])
        else:
            lead_val = min(0.6, 0.05 * years_exp + 0.05 * row['career_count'])
        leadership_scores.append(lead_val)
        
    df['llm_score'] = llm_scores
    df['retrieval_score'] = retrieval_scores
    df['vector_db_score'] = vector_db_scores
    df['backend_score'] = backend_scores
    df['leadership_score'] = leadership_scores
    
    # 6. Career Growth Score (0-1 scale)
    # Combines experience_score, interview completion and response rate
    df['career_growth'] = np.clip(
        df['experience_score'] * 0.5 + 
        df['interview_completion'] * 0.3 + 
        df['response_rate'] * 0.2, 
        0.0, 1.0
    )
    
    # Keep only the columns specified in Person 1's output schema
    person1_columns = [
        'candidate_id', 'years_experience', 'llm_score', 'retrieval_score',
        'vector_db_score', 'backend_score', 'career_growth', 'leadership_score', 'availability_score'
    ]
    df_engineered = df[person1_columns]
    
    # Save to Parquet
    df_engineered.to_parquet(parquet_output_path, index=False)
    print(f"Feature engineering completed. Parquet file saved at: {parquet_output_path}")

def extract_skills_from_jd(jd_text):
    SKILL_KEYWORDS = {
        "large language models": ["large language models", "llm", "llms"],
        "transformer models": ["transformer", "transformers"],
        "model fine tuning": ["fine tuning", "finetuning", "fine-tuning"],
        "parameter efficient fine tuning": ["peft", "lora", "qlora"],
        "sentence transformers": ["sentence transformers", "sentence-transformers"],
        "natural language processing": ["nlp", "natural language processing"],
        "information retrieval": ["information retrieval", "retrieval"],
        "matching systems": ["matching systems", "matching"],
        "search systems": ["search systems", "search engines", "search infrastructure"],
        "ranking systems": ["ranking systems", "ranking"],
        "embeddings": ["embeddings", "embedding"],
        "ai evaluation": ["ai evaluation", "model evaluation"],
        "vector databases": ["vector databases", "vector database", "vector db", "pinecone", "qdrant", "milvus", "weaviate"],
        "vector indexes": ["vector indexes", "vector index", "hnsw"],
        "python": ["python"],
        "distributed systems": ["distributed systems", "distributed architecture"],
        "go": ["go", "golang"],
        "kubernetes": ["kubernetes", "k8s"],
        "docker": ["docker", "containerization"],
        "sql": ["sql", "postgresql", "mysql"],
        "aws": ["aws", "amazon web services"],
        "gcp": ["gcp", "google cloud"]
    }
    
    extracted = set()
    jd_lower = jd_text.lower()
    for skill_name, aliases in SKILL_KEYWORDS.items():
        for alias in aliases:
            if alias in jd_lower:
                extracted.add(skill_name)
                break
    return extracted

def run_ranker(data_dir, output_dir):
    """
    Person 4 Ranking Engine.
    Loads and merges all datasets, runs formulas for technical_fit, talent_dna, and final_score,
    ranks the candidates, and outputs ranked_candidates.csv.
    """
    print("Initializing Candidate Ranking Engine...")
    
    raw_features_path = os.path.join(data_dir, "candidate_features_raw.csv")
    explanations_json_path = os.path.join(data_dir, "candidate_explanations.json")
    parquet_path = os.path.join(data_dir, "candidate_features.parquet")
    semantic_scores_path = os.path.join(data_dir, "semantic_scores.csv")
    behavior_scores_path = os.path.join(data_dir, "behavior_scores.csv")
    ranked_output_path = os.path.join(output_dir, "ranked_candidates.csv")
    
    # Pre-step: Run feature engineering if parquet file doesn't exist
    if not os.path.exists(parquet_path):
        engineer_features(raw_features_path, explanations_json_path, parquet_path)
        
    # Load candidate features (Person 1)
    df_features = pd.read_parquet(parquet_path)
    
    # Load semantic scores (Person 2) dynamically if pasted_jd.txt exists
    pasted_jd_path = os.path.join(data_dir, "pasted_jd.txt")
    if os.path.exists(pasted_jd_path):
        print("Found pasted Job Description. Calculating dynamic semantic scores...")
        try:
            with open(pasted_jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
            jd_skills = extract_skills_from_jd(jd_text)
            if not jd_skills:
                jd_skills = {"python", "large language models"} # Default fallback
                
            with open(explanations_json_path, 'r', encoding='utf-8') as f:
                explanations = json.load(f)
            skills_map = {item['candidate_id']: set(item['matched_skills']) for item in explanations}
            
            dynamic_scores = {}
            for cand_id in df_features['candidate_id']:
                cand_skills = skills_map.get(cand_id, set())
                cand_skills_lower = {s.lower() for s in cand_skills}
                jd_skills_lower = {s.lower() for s in jd_skills}
                
                intersection = cand_skills_lower & jd_skills_lower
                score = len(intersection) / len(jd_skills_lower)
                dynamic_scores[cand_id] = score
                
            df_semantic = pd.DataFrame(list(dynamic_scores.items()), columns=['candidate_id', 'semantic_score'])
        except Exception as e:
            print(f"Error calculating dynamic semantic scores: {e}. Falling back to static scores.")
            df_semantic = pd.read_csv(semantic_scores_path)
            df_semantic = df_semantic.rename(columns={'score': 'semantic_score'})
    else:
        df_semantic = pd.read_csv(semantic_scores_path)
        df_semantic = df_semantic.rename(columns={'score': 'semantic_score'})
    
    # Load behavior & trust scores (Person 3)
    df_behavior = pd.read_csv(behavior_scores_path)
    
    # Merge datasets
    # Since semantic scores are only calculated for top candidates (50),
    # an outer join will keep all candidates, filling missing semantic scores with 0.
    # An inner join will focus only on candidates with computed semantic scores.
    # We outer-join here to keep the full dataset, but we will focus on the top 50 in outputs.
    df_merged = pd.merge(df_features, df_behavior, on='candidate_id', suffixes=('', '_dup'))
    # Clean up duplicate columns if any
    df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]
    
    df_final = pd.merge(df_merged, df_semantic[['candidate_id', 'semantic_score']], on='candidate_id', how='left')
    df_final['semantic_score'] = df_final['semantic_score'].fillna(0.0)
    
    # Normalize semantic_score if it is on 0-100 scale
    if df_final['semantic_score'].max() > 1.0:
        df_final['semantic_score'] = df_final['semantic_score'] / 100.0
        
    # Technical Fit Formula
    df_final['technical_fit'] = (
        0.30 * df_final['llm_score'] +
        0.30 * df_final['retrieval_score'] +
        0.20 * df_final['vector_db_score'] +
        0.20 * df_final['backend_score']
    )
    
    # Talent DNA Formula
    df_final['talent_dna'] = (
        0.30 * df_final['technical_fit'] +
        0.25 * df_final['semantic_score'] +
        0.20 * df_final['behavior_score'] +
        0.10 * df_final['career_growth'] +
        0.05 * df_final['leadership_score'] +
        0.05 * df_final['availability_score'] +
        0.05 * df_final['trust_score']
    )
    
    # Final Score Formula (Minus Honeypot Penalty)
    df_final['final_score'] = df_final['talent_dna'] - df_final['honeypot_penalty']
    
    # Rank candidates in descending order of final_score
    df_final = df_final.sort_values(by='final_score', ascending=False).reset_index(drop=True)
    df_final['rank'] = df_final.index + 1
    
    # Merge current_title and current_company from clean_candidates.csv to include in rankings output
    clean_candidates_path = os.path.join(data_dir, "clean_candidates.csv")
    if os.path.exists(clean_candidates_path):
        try:
            df_clean = pd.read_csv(clean_candidates_path)
            df_final = pd.merge(df_final, df_clean[['candidate_id', 'current_title', 'current_company']], on='candidate_id', how='left')
        except Exception as e:
            print(f"Error merging current_title/company: {e}")
            
    # Export to CSV
    os.makedirs(output_dir, exist_ok=True)
    df_final.to_csv(ranked_output_path, index=False)
    print(f"Ranking complete! Ranked candidates exported to: {ranked_output_path}")
    print(f"Top 5 Ranked Candidates:")
    print(df_final[['rank', 'candidate_id', 'technical_fit', 'semantic_score', 'talent_dna', 'final_score']].head(5))
    return df_final

if __name__ == "__main__":
    DATA_DIR = os.path.join(BASE_DIR, "data")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    run_ranker(DATA_DIR, OUTPUT_DIR)
