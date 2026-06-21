import json

with open(
    "sample_candidates.json",
    "r",
    encoding="utf-8"
) as f:
    candidates = json.load(f)

max_profile_views = 0
max_recruiter_saves = 0
max_search_appearance = 0

for candidate in candidates:

    signals = candidate.get("redrob_signals",{})

    max_profile_views = max(max_profile_views,signals.get("profile_views_received_30d",0))

    max_recruiter_saves = max(max_recruiter_saves,signals.get("saved_by_recruiters_30d",0))

    max_search_appearance = max(max_search_appearance,signals.get("search_appearance_30d",0))

print("MAX_PROFILE_VIEWS =", max_profile_views)
print("MAX_RECRUITER_SAVES =", max_recruiter_saves)
print("MAX_SEARCH_APPEARANCE =", max_search_appearance)