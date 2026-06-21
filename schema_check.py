import json

with open(
    "sample_candidates.json",
    "r",
    encoding="utf-8"
) as f:
    candidates = json.load(f)

candidate = candidates[0]

print("\nTOP LEVEL KEYS")
print(candidate.keys())

print("\nPROFILE KEYS")
print(candidate["profile"].keys())

print("\nEDUCATION")
print(candidate["education"][0])

print("\nCAREER HISTORY")
print(candidate["career_history"][0])

print("\nSKILLS")
print(candidate["skills"][:5])

print("\nREDROB SIGNALS")
print(candidate["redrob_signals"].keys())