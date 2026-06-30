# 🧠 TalentMindAI — AI-Powered Recruitment Intelligence Platform

> An end-to-end AI recruitment pipeline that ranks **100,000 candidates** against any Job Description using multi-dimensional scoring across technical fit, semantic relevance, behavioral engagement, and trust verification — with a premium recruiter dashboard built in Streamlit.

---

## 🚀 Quick Start

```bash
cd project
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📌 Problem Statement

Recruiters manually screen thousands of resumes — a slow, biased, and error-prone process. TalentMindAI solves this by combining **4 independent AI scoring engines** into one unified ranking system that evaluates every candidate from multiple dimensions and surfaces the best matches instantly.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECRUITER DASHBOARD (app.py)                  │
│  ┌───────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │ Dashboard │ Upload & │ Rankings │ Insights │  Analytics   │  │
│  │  Overview │Configure │  Table   │ Deep Dive│  Charts      │  │
│  └───────────┴──────────┴──────────┴──────────┴──────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  ranker.py  │  ◄── Ranking Engine (Person 4)
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐
   │  Person 1   │  │  Person 2  │  │  Person 3   │
   │  Feature    │  │  NLP &     │  │  Behavior & │
   │ Engineering │  │  Semantic  │  │  Trust      │
   │             │  │  Matching  │  │  Engines    │
   └─────────────┘  └────────────┘  └─────────────┘
```

---

## 📊 Scoring & Ranking Method

### Technical Fit Score (Feature Engineer)

Measures raw technical skill level from candidate profile data:

```
Technical Fit = 0.30 × LLM Score
             + 0.30 × Retrieval Score
             + 0.20 × Vector DB Score
             + 0.20 × Backend Score
```

### Semantic Match Score (Semantic Matching Pipeline Developer)

Measures skill alignment with the pasted Job Description:

```
Semantic Score = (Candidate skills matching JD keywords) / (Total JD keywords)
```

> This score **recalculates dynamically** when you paste a new Job Description and trigger the pipeline.

### Behavior Score (Behavior and Trust Engine Developer)

Measures candidate engagement: response rate, activity frequency, recruiter saves, and platform interaction patterns.

### Trust Score (Behavior and Trust Engine Developer)

Verifies profile authenticity: checks for skill inflation, timeline inconsistencies, and honeypot trap triggers.

### Talent DNA Score (Final Composite)

| Component | Weight | Source |
|-----------|--------|--------|
| Technical Fit | 30% | Feature Engineer — LLM, Retrieval, VectorDB, Backend scores |
| Semantic Match | 25% | Semantic Matching Pipeline Developer — NLP keyword matching against JD |
| Behavior Score | 20% |Behavior and Trust Engine Developer — Engagement, response rate, activity |
| Career Growth | 10% | Feature Engineer — Career trajectory analysis |
| Leadership | 5% | Feature Engineer — Leadership experience and seniority |
| Availability | 5% | Behavior and Trust Engine Developer — Notice period and join readiness |
| Trust Score | 5% | Behavior and Trust Engine Developer — Profile verification and authenticity |

### Final Score

```
Final Score = Talent DNA − Honeypot Penalty
```

**Honeypot Penalty** (0 to 0.50): Candidates who applied to fake trap job postings (designed to catch keyword-stuffers) get their score reduced, pushing fraudulent profiles to the bottom.

All 100,000 candidates are sorted by Final Score in descending order → Rank #1 = best match.

---

## 🖥️ Dashboard Pages (5 Pages)

| Page | Description |
|------|-------------|
| **Dashboard** | Overview metrics — total candidates scored, average Talent DNA, top 5 performers with scores |
| **Upload & Configure** | Paste any Job Description text, validate it, and trigger the AI ranking pipeline |
| **Rankings** | Full ranked candidate table with sorting (by overall score, semantic, behavior, technical fit), search, and CSV export |
| **Insights** | Candidate DNA Deep Dive — profile card, radar chart (7 dimensions), key strengths, potential risks, experience timeline |
| **Analytics** | Score distribution histograms, correlation heatmaps, trust flag breakdown charts |

### UI Features
- 🌗 **Dark / Light Mode** toggle
- 🔍 **Search** candidates by ID
- 📊 **Sort** by any scoring dimension
- 📥 **CSV Export** of full ranked list
- 🎯 **Real candidate names** loaded from 100K dataset
- ✅ **JD Validation** — blocks empty or non-technical job descriptions

---

## 📂 Project Structure

```
project/
│
├── app.py                     # Streamlit dashboard — 5 pages, dark/light mode (Person 4)
├── ranker.py                  # Ranking engine — feature engineering + scoring + merging (Person 4)
├── reason_generator.py        # Explainability — strengths & risks generator (Person 4)
├── integration_test.py        # 4 integration tests with deterministic assertions (Person 4)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── behavior_engine.py         # Behavioral scoring engine (Person 3)
├── trust_engine.py            # Trust verification engine (Person 3)
│
├── data/
│   ├── candidate_features_raw.csv    # 100K candidates × raw feature scores (Person 1)
│   ├── clean_candidates.csv          # 100K candidates × profile info, title, company, skills (Person 1)
│   ├── semantic_scores.csv           # Top-50 semantic match scores (Person 2)
│   ├── candidate_explanations.json   # Skill match details per candidate (Person 2)
│   ├── jd_intelligence.json          # Parsed JD metadata (Person 2)
│   ├── behavior_scores.csv           # 100K candidates × behavior + trust scores (Person 3)
│   └── candidate_metadata.csv        # 100K candidate names & locations cache (Person 4)
│
└── output/
    └── ranked_candidates.csv         # Final ranked output — 100K rows × 22 columns (auto-generated)
```

---

## 🧪 Integration Tests

```bash
cd project
python integration_test.py
```

| # | Test Scenario | What it Validates |
|---|---------------|-------------------|
| 1 | **Perfect Match** | Candidate with highest technical + semantic scores ranks #1 |
| 2 | **Hidden Talent** | Candidates with high semantic affinity surface in top 10 even with lower technical scores |
| 3 | **Keyword Spammer** | Honeypot penalty suppresses fraudulent profiles far below legitimate candidates |
| 4 | **Behavioral Twins** | Two candidates with similar skills → behavior score acts as the tiebreaker |

```
==================================================
         ALL INTEGRATION TESTS PASSED (4/4)
==================================================
```

---

## 🔑 Key Features

| Feature | Description |
|---------|-------------|
| **Dynamic JD Matching** | Paste any Job Description → rankings recalculate in real-time |
| **100K Scale** | Handles 100,000 candidate profiles with sub-second dashboard loads |
| **Explainability** | Every candidate gets human-readable Key Strengths and Potential Risks |
| **Fraud Detection** | Honeypot mechanism catches and penalizes keyword stuffers |
| **Radar Chart** | 7-dimension visual DNA fingerprint per candidate |
| **Dark/Light Mode** | Premium UI with full theme toggle |
| **CSV Export** | Download the complete ranked list for offline review |
| **Real Names** | Displays actual anonymized names from the 100K dataset |

---

## 👥 Team Contributions

| Person | Role | Key Deliverables |
|--------|------|------------------|
| **Kanishq Joshi** | Feature Engineering | `candidate_features_raw.csv`, `clean_candidates.csv` — raw skill scores and cleaned profiles for 100K candidates |
| **Soham Balsaraf** | NLP & Semantic Matching | `semantic_scores.csv`, `candidate_explanations.json` — skill extraction and JD-to-candidate matching |
| **Om Karanje** | Behavior & Trust Engines | `behavior_scores.csv`, `behavior_engine.py`, `trust_engine.py` — engagement scoring and fraud detection |
| **Sharad Shinde** | Ranking Engine & Dashboard | `app.py`, `ranker.py`, `reason_generator.py`, `integration_test.py` — final ranking algorithm, explainability, Streamlit UI, and testing |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit, Plotly, Custom HTML/CSS |
| Backend | Python 3.13, Pandas, NumPy |
| Data | CSV, JSON, JSONL, Parquet |
| UI Components | streamlit-option-menu, streamlit-lottie |
| Testing | Custom integration test suite |

---

## 📄 License

This project was built for hackathon demonstration purposes.
