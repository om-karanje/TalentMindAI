def generate_explanations(candidate_row):
    """
    Rule-based explainability engine for candidate ranking.
    Analyzes a candidate record (pandas Series or dict) and generates a list of 
    key strengths and risk indicators.
    
    Expected keys in candidate_row:
        - semantic_score (0-1 scale)
        - llm_score (0-1 scale)
        - technical_fit (0-1 scale)
        - behavior_score (0-1 scale)
        - saved_by_recruiters
        - response_rate (0-1 scale)
        - leadership_score (0-1 scale)
        - years_experience
        - notice_period (in days)
        - availability_score (0-1 scale)
        - trust_score (0-1 scale)
        - honeypot_penalty
        - career_growth (0-1 scale)
    """
    strengths = []
    risks = []
    
    # --- STRENGTHS RULES ---
    
    # 1. Technical Fit
    tech_fit = candidate_row.get("technical_fit", 0)
    if tech_fit >= 0.60:
        strengths.append(f"Strong Technical Fit ({tech_fit:.0%})")
    elif tech_fit >= 0.40:
        strengths.append(f"Moderate Technical Fit ({tech_fit:.0%})")
    
    # 2. Semantic Match
    sem_score = candidate_row.get("semantic_score", 0)
    if sem_score > 1.0:
        sem_score = sem_score / 100.0
    if sem_score >= 0.50:
        strengths.append(f"Strong Semantic Match ({sem_score:.0%})")
    elif sem_score >= 0.20:
        strengths.append(f"Partial Semantic Match ({sem_score:.0%})")
        
    # 3. LLM Experience
    llm_score = candidate_row.get("llm_score", 0)
    if llm_score >= 0.50:
        strengths.append(f"Strong LLM Experience ({llm_score:.0%})")
    elif llm_score >= 0.25:
        strengths.append(f"Moderate LLM Experience ({llm_score:.0%})")
        
    # 4. Career Growth
    career_growth = candidate_row.get("career_growth", 0)
    if career_growth >= 0.60:
        strengths.append(f"Strong Career Growth Trajectory ({career_growth:.0%})")
        
    # 5. Behavioral Engagement
    behavior = candidate_row.get("behavior_score", 0)
    if behavior >= 0.60:
        strengths.append(f"High Behavioral Engagement ({behavior:.0%})")
    elif behavior >= 0.40:
        strengths.append(f"Moderate Behavioral Engagement ({behavior:.0%})")
        
    # 6. Recruiter Engagement
    saved = candidate_row.get("saved_by_recruiters", 0)
    resp_rate = candidate_row.get("response_rate", 0)
    if saved >= 5 or resp_rate >= 0.50:
        strengths.append(f"Active Recruiter Engagement ({saved} saves, {resp_rate:.0%} resp)")
        
    # 7. Leadership Experience
    lead_score = candidate_row.get("leadership_score", 0)
    years_exp = candidate_row.get("years_experience", 0)
    if lead_score >= 0.50 or years_exp >= 8.0:
        strengths.append(f"Leadership Experience ({years_exp:.1f} yrs experience)")
    
    # 8. High Trust Score
    trust = candidate_row.get("trust_score", 0)
    if trust >= 0.80:
        strengths.append(f"Highly Trusted Profile ({trust:.0%} trust score)")
        
    # 9. High Availability
    avail_score = candidate_row.get("availability_score", 0)
    if avail_score >= 0.70:
        strengths.append(f"High Availability ({avail_score:.0%})")
        
    # --- RISKS RULES ---
    
    # 1. Long Notice Period
    notice = candidate_row.get("notice_period", 0)
    if notice >= 90:
        risks.append(f"Long Notice Period ({notice} days)")
    elif notice >= 60:
        risks.append(f"Moderate Notice Period ({notice} days)")
        
    # 2. Low Availability
    if avail_score < 0.40:
        risks.append(f"Low Availability ({avail_score:.0%})")
        
    # 3. Low Technical Fit
    if tech_fit < 0.25:
        risks.append(f"Low Technical Fit ({tech_fit:.0%})")
        
    # 4. Low Semantic Match
    if sem_score < 0.10:
        risks.append(f"Low JD Alignment ({sem_score:.0%} semantic match)")
        
    # 5. Low Leadership Experience  
    if lead_score < 0.25:
        risks.append(f"Low Leadership Score ({lead_score:.0%})")
        
    # 6. Low Trust Score
    if trust < 0.50:
        risks.append(f"Low Trust Score ({trust:.0%})")
        
    # 7. Honeypot Penalty Applied
    penalty = candidate_row.get("honeypot_penalty", 0)
    if penalty > 0:
        risks.append(f"Honeypot Penalty Applied (-{penalty:.2f} score reduction)")
        
    # 8. Low Recruiter Interest
    if saved <= 1 and resp_rate < 0.30:
        risks.append(f"Low Recruiter Interest ({saved} saves, {resp_rate:.0%} response rate)")
        
    # 9. Limited Experience
    if years_exp < 2.0:
        risks.append(f"Limited Experience ({years_exp:.1f} years)")
        
    return {
        "candidate_id": candidate_row.get("candidate_id"),
        "strengths": strengths,
        "risks": risks
    }
