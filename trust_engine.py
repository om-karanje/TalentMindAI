"""
Generates:
1. trust_score
2. honeypot_penalty
3. trust_flags
"""

from datetime import datetime

# HELPERS
def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

def clamp(value, min_val=0.0, max_val=1.0):
    return max(min_val, min(value, max_val))

# VERIFICATION SCORE
def calculate_verification_score(signals):

    email = 1 if signals.get("verified_email",False) else 0

    phone = 1 if signals.get("verified_phone",False) else 0

    linkedin = 1 if signals.get("linkedin_connected",False) else 0

    score = (0.4 * email +0.4 * phone +0.2 * linkedin)
    return score

# PROFILE COMPLETENESS PENALTY
def profile_completeness_penalty(signals):

    completeness = safe_float(signals.get("profile_completeness_score",0))

    if completeness < 40:
        return 0.20

    elif completeness < 60:
        return 0.10

    return 0.0

# SKILL INFLATION CHECK
def skill_inflation_penalty(skills,years_exp):

    if years_exp <= 0:
        return 0.30

    skill_count = len(skills)

    ratio = (skill_count /years_exp)

    if ratio > 7:
        return 0.25

    elif ratio > 5:
        return 0.10

    return 0.0

# SKILL DURATION CHECK
def skill_duration_penalty(skills,years_exp):

    penalty = 0.0

    max_possible_months = (years_exp * 12)

    for skill in skills:
        duration = safe_float(skill.get("duration_months",0))

        if duration > (max_possible_months + 24):
            penalty += 0.05

    return min(penalty,0.20)

# CAREER CONTRADICTION
def career_contradiction_penalty(profile,skills):

    title = str(profile.get("current_title","")).lower()

    business_titles = [
        "marketing",
        "sales",
        "hr",
        "recruiter",
        "accountant",
        "finance"
    ]

    ai_keywords = [
        "llm",
        "rag",
        "retrieval",
        "ranking",
        "pinecone",
        "qdrant",
        "vector",
        "fine-tuning",
        "transformer"
    ]

    title_is_business = any(
        keyword in title
        for keyword in business_titles
    )

    ai_skill_count = 0

    for skill in skills:
        skill_name = str(skill.get("name","")).lower()

        if any(
            keyword in skill_name
            for keyword in ai_keywords
        ):
            ai_skill_count += 1

    if title_is_business and ai_skill_count >= 3:
        return 0.30

    return 0.0

# EDUCATION TIMELINE CHECK
def education_timeline_penalty(education,years_exp):

    if not education:
        return 0.0

    latest_end_year = max(edu.get("end_year",2000)for edu in education)

    current_year = datetime.now().year

    possible_exp = (current_year -latest_end_year)

    if years_exp > (possible_exp + 2):
        return 0.30

    return 0.0

# CAREER TIMELINE CHECK
def career_timeline_penalty(career_history,years_exp):

    total_months = 0

    for job in career_history:

        total_months += safe_float(job.get("duration_months",0))

    career_years = (total_months / 12)

    if abs(career_years -years_exp) > 3:
        return 0.20

    return 0.0

# WEAK EVIDENCE CHECK
def weak_evidence_penalty(profile,signals):

    title = str(profile.get("current_title","")).lower()

    github_score = safe_float(signals.get("github_activity_score",0))

    assessments = signals.get("skill_assessment_scores",{})

    ai_keywords = [
        "engineer",
        "ml",
        "machine learning",
        "data scientist",
        "ai"
    ]

    technical_role = any(
        keyword in title
        for keyword in ai_keywords
    )

    if (
        technical_role
        and github_score == 0
        and len(assessments) == 0
    ):
        return 0.15

    return 0.0

# TRUST SCORE
def calculate_trust_score(candidate):

    profile = candidate.get("profile",{})

    skills = candidate.get("skills",[])

    education = candidate.get("education",[])

    career_history = candidate.get("career_history",[])

    signals = candidate.get("redrob_signals",{})

    years_exp = safe_float(profile.get("years_of_experience",0))

    verification_score = (calculate_verification_score(signals))

    penalties = []
    penalties.append(profile_completeness_penalty(signals))
    penalties.append(skill_inflation_penalty(skills,years_exp))
    penalties.append(skill_duration_penalty(skills,years_exp))
    penalties.append(career_contradiction_penalty(profile,skills))
    penalties.append(education_timeline_penalty(education,years_exp))
    penalties.append(career_timeline_penalty(career_history,years_exp))
    penalties.append(weak_evidence_penalty(profile,signals))

    total_penalty = sum(penalties)

    trust_score = (verification_score -total_penalty)
    trust_score = clamp(trust_score)

    honeypot_penalty = min(total_penalty,1.0)

    return (round(trust_score,4), round(honeypot_penalty,4))

# TRUST FLAGS
def generate_trust_flags(candidate):

    flags = []

    signals = candidate.get("redrob_signals",{})

    if signals.get("verified_email",False):
        flags.append("verified_email")

    if signals.get("verified_phone",False):
        flags.append("verified_phone")

    if signals.get("linkedin_connected",False):
        flags.append("linkedin_connected")

    return flags

# MAIN GENERATOR
def generate_trust_features(candidate):
    trust_score, honeypot_penalty = (calculate_trust_score(candidate))

    return {
        "candidate_id":candidate.get("candidate_id"),
        "trust_score":trust_score,
        "honeypot_penalty":honeypot_penalty,
        "trust_flags":generate_trust_flags(candidate)
    }

# TEST
if __name__ == "__main__":

    import json
    with open("sample_candidates.json","r",encoding="utf-8") as f:
        candidates = json.load(f) 
    
    for candidate in candidates[:20]:
        result = (generate_trust_features(candidate))

        print(result)