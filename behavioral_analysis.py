"""
Generates:
1. behavior_score
2. availability_score
3. market_interest_score
for every candidate.
"""

from datetime import datetime
import numpy as np

MAX_PROFILE_VIEWS = 194
MAX_RECRUITER_SAVES = 18
MAX_SEARCH_APPEARANCE = 778

# HELPER FUNCTIONS
def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

def normalize(value, min_val, max_val):
    """ Min-Max normalization. Returns value between 0 and 1."""
    value = max(min_val, min(value, max_val))

    if max_val == min_val: 
        return 0.0

    return (value - min_val) / (max_val - min_val)

# ACTIVITY SCORE
def calculate_activity_score(last_active_date):
    """Converts last active date into activity score. Recent activity = higher score."""

    try:
        last_active = datetime.strptime(last_active_date,"%Y-%m-%d")

        today = datetime.today()

        days_since_active = (today - last_active).days

    except:
        return 0.3

    if days_since_active <= 7:
        return 1.0

    elif days_since_active <= 30:
        return 0.8

    elif days_since_active <= 90:
        return 0.5

    elif days_since_active <= 180:
        return 0.3

    else:
        return 0.1

# OFFER ACCEPTANCE SCORE
def calculate_offer_acceptance_score(offer_acceptance_rate):
    """Redrob uses: -1 = No historical offer data. 
    We treat it neutrally."""

    if offer_acceptance_rate == -1:
        return 0.5

    return max(0.0,min(1.0, offer_acceptance_rate))

# NOTICE PERIOD SCORE
def calculate_notice_period_score(notice_period_days):
    """Lower notice period is better."""

    days = safe_float(notice_period_days,180)

    if days <= 30:
        return 1.0

    elif days <= 60:
        return 0.8

    elif days <= 90:
        return 0.6

    elif days <= 120:
        return 0.4

    else:
        return 0.2

# OPEN TO WORK SCORE
def calculate_open_to_work_score(open_to_work_flag):
    return 1.0 if open_to_work_flag else 0.5

# MARKET INTEREST SCORE
def calculate_market_interest_score(signals):
    """Recruiter demand.
    Uses:
    profile_views_received_30d
    saved_by_recruiters_30d
    search_appearance_30d"""

    profile_views = safe_float(signals.get("profile_views_received_30d",0))

    recruiter_saves = safe_float(signals.get("saved_by_recruiters_30d",0))

    search_appearance = safe_float(signals.get("search_appearance_30d",0))

    profile_views_norm = (profile_views /MAX_PROFILE_VIEWS)

    recruiter_saves_norm = (recruiter_saves /MAX_RECRUITER_SAVES)

    search_appearance_norm = (search_appearance /MAX_SEARCH_APPEARANCE)

    market_score = (0.25 * profile_views_norm +0.40 * recruiter_saves_norm +0.35 * search_appearance_norm)

    return round(market_score, 4)

# BEHAVIOR SCORE
def calculate_behavior_score(signals):
    """Hiring readiness score.
    Range: 0 - 1"""

    recruiter_response_rate = safe_float(signals.get("recruiter_response_rate",0))

    interview_completion_rate = safe_float(signals.get("interview_completion_rate",0))

    profile_completeness = normalize(safe_float(signals.get("profile_completeness_score",0)),0,100)

    activity_score = calculate_activity_score(signals.get("last_active_date",""))

    offer_acceptance_score = (calculate_offer_acceptance_score(signals.get("offer_acceptance_rate",-1)))

    behavior_score = (0.30 * recruiter_response_rate +0.25 * interview_completion_rate +0.20 * offer_acceptance_score +0.15 * activity_score +0.10 * profile_completeness)

    return round(behavior_score,4)

# AVAILABILITY SCORE
def calculate_availability_score(signals):
    """How easily candidate can join."""

    notice_period_score = (calculate_notice_period_score(signals.get("notice_period_days",180)))

    open_to_work_score = (calculate_open_to_work_score(signals.get("open_to_work_flag",False)))

    activity_score = (calculate_activity_score(signals.get("last_active_date","")))

    availability_score = (0.50 * notice_period_score +0.30 * open_to_work_score +0.20 * activity_score)

    return round(availability_score,4)

# MAIN FEATURE GENERATOR
def generate_behavior_features(candidate):
    """Returns all behavior features."""

    signals = candidate.get("redrob_signals",{})

    behavior_score = (calculate_behavior_score(signals))

    availability_score = (calculate_availability_score(signals))

    market_interest_score = (calculate_market_interest_score(signals))

    return {
        "candidate_id":candidate.get("candidate_id"),
        "behavior_score":behavior_score,
        "availability_score":availability_score,
        "market_interest_score":market_interest_score
    }

# TEST
if __name__ == "__main__":

    import json

    with open("sample_candidates.json","r",encoding="utf-8") as f:

        candidates = json.load(f)

    for candidate in candidates[:20]:

        result = generate_behavior_features(candidate)

        print("\n")
        print(candidate["candidate_id"])
        print(result)

        scores = []