#  TalentMindAI –  Behavioral Intelligence & Trust Engine

This module implements the **Behavioral Intelligence** and **Trust Intelligence** components for the **Redrob Intelligent Candidate Discovery & Ranking Challenge**.

Unlike traditional Applicant Tracking Systems (ATS) that rely only on technical skills or keyword matching, this module evaluates candidates based on **behavioral engagement, recruiter interaction, profile credibility, and fraud detection**, enabling a more holistic and trustworthy hiring process.

---

#  Responsibilities

This module is responsible for:
- Behavioral Feature Engineering
- Availability Scoring
- Market Interest Analysis
- Trust Score Generation
- Honeypot Detection
- Profile Verification
- Candidate Feature Generation
- Feature Export for Final Ranking

The generated features are consumed by the **Talent DNA Ranking Engine** .

---

#  Installation

Clone the repository and create a virtual environment.

```bash
cd project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS

```bash
source .venv/bin/activate
```

---

#  Dataset

Supported datasets

```
sample_candidates.json
candidates.jsonl
```

Place the dataset inside the project directory or update the path inside the scripts.

---

#  Behavioral Intelligence Pipeline

```
Candidate Dataset
        │
        ▼
Behavior Engine
        │
        ├────────────► Behavior Score
        │
        ├────────────► Availability Score
        │
        └────────────► Market Interest Score
```

---

#  Trust Intelligence Pipeline

```
Candidate Profile
        │
        ▼
Verification Checks
        │
Timeline Validation
        │
Skill Inflation Detection
        │
Career Consistency
        │
Profile Completeness
        │
        ▼
Trust Engine
        │
        ├────────────► Trust Score
        │
        ├────────────► Honeypot Penalty
        │
        └────────────► Trust Flags
```

---

#  Implemented Modules

## 1. behavior_engine.py

Generates behavioral intelligence features using candidate engagement signals.

### Output Features

| Feature | Description |
|----------|-------------|
| behavior_score | Overall behavioral quality of the candidate |
| availability_score | Candidate's readiness to join |
| market_interest_score | Recruiter demand based on platform engagement |

---

### Signals Used

Behavior Score

- Recruiter Response Rate
- Interview Completion Rate
- Offer Acceptance Rate
- GitHub Activity
- Profile Completeness

Availability Score

- Notice Period
- Open To Work Flag
- Last Active Date

Market Interest Score

- Profile Views
- Saved by Recruiters
- Search Appearance

---

## 2. trust_engine.py

Evaluates profile authenticity and detects suspicious candidates.

### Generated Features

| Feature | Description |
|----------|-------------|
| trust_score | Overall credibility score |
| honeypot_penalty | Fraud penalty |
| trust_flags | Explainability flags |

---

### Verification Signals

- Verified Email
- Verified Phone
- LinkedIn Connected
- Profile Completeness

---

### Fraud Detection

The Trust Engine checks for:

- Skill Inflation
- Impossible Career Timelines
- Career Contradictions
- Unrealistic Experience Claims
- Weak Technical Evidence
- Profile Inconsistencies

---

## 3. generate_features.py

Combines outputs from the Behavior Engine and Trust Engine.

Generated CSV

```
candidate_features.csv
```

Contains

```
candidate_id
behavior_score
availability_score
market_interest_score
trust_score
honeypot_penalty
trust_flags
```

---

## 4. market_stats.py

Computes normalization statistics from the complete dataset.

Calculates

```
MAX_PROFILE_VIEWS
MAX_RECRUITER_SAVES
MAX_SEARCH_APPEARANCE
```

These values are used for market interest normalization.

---

#  Project Structure

```
project/

│
├── behavior_engine.py
├── trust_engine.py
├── generate_features.py
├── market_stats.py
├── candidate_features.csv
├── sample_candidates.json
├── candidates.jsonl
└── README.md
```

---

#  Running the Module

## Generate Candidate Features

```bash
python generate_features.py
```

Output

```
candidate_features.csv
```

---

## Compute Market Statistics

```bash
python market_stats.py
```

Outputs

```
MAX_PROFILE_VIEWS
MAX_RECRUITER_SAVES
MAX_SEARCH_APPEARANCE
```

---

#  Generated Features

Behavior Features

| Feature | Range |
|----------|-------|
| behavior_score | 0 – 1 |
| availability_score | 0 – 1 |
| market_interest_score | 0 – 1 |

---

Trust Features

| Feature | Range |
|----------|-------|
| trust_score | 0 – 1 |
| honeypot_penalty | 0 – 1 |

---

# 📈 Sample Statistics

Generated on the 1000 candidate validation dataset.

| Feature | Min | Max | Average |
|----------|-----|-----|---------|
| Behavior Score | 0.2272 | 0.7423 | 0.4854 |
| Availability Score | 0.2700 | 0.9000 | 0.5741 |
| Market Interest Score | 0.0052 | 0.4948 | 0.0956 |
| Trust Score | 0.1100 | 1.0000 | 0.7966 |
| Honeypot Penalty | 0.0000 | 0.8000 | 0.1433 |

---

# 🔗 Integration

This module is designed to integrate seamlessly with the other TalentMindAI components.

## Input

Consumes normalized candidate profiles generated by **Person 1**.

---

## Output

Provides behavioral and trust features for the **Ranking Engine**.

```
candidate_features.csv
```

---

## Used By

### Semantic Matching Pipeline Developer

Can use behavioral insights for semantic explainability.

---

### Ranking + Dashboard Designer

Consumes

- behavior_score
- availability_score
- market_interest_score
- trust_score
- honeypot_penalty
- trust_flags

to compute the final **Talent DNA Score**.

---

#  Design Principles

This module follows five design principles.

### Explainability

Every generated score corresponds to interpretable recruiter signals.

---

### Scalability

Optimized for processing **100,000+ candidates**.

---

### Modularity

Behavior and Trust engines can be executed independently.

---

### CPU Friendly

No GPU is required.

---

### Lightweight

Uses rule-based scoring instead of heavy ML models for fast execution.

---

#  Outputs

Generated files

```
candidate_features.csv
```

Used directly by the Ranking Engine.

---

#  Author

**Om Karanje : Behavior and Trust Engine Developer**

Behavioral Intelligence & Trust Intelligence Engineer

TalentMindAI – AI Powered Intelligent Candidate Discovery & Ranking Platform

Redrob Intelligent Candidate Discovery & Ranking Challenge
