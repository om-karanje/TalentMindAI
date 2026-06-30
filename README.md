# TalentMindAI - Feature Engineering Pipeline

This module implements the **Scope of Feature and Data Engineer** for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

Its responsibility is to transform raw candidate profiles into structured candidate intelligence that can be consumed by the Semantic Matching Engine, Behavioral Intelligence Engine, and Final Ranking Engine.

---

# Responsibilities

This module performs:

- Candidate Dataset Loading
- Candidate Schema Validation
- Data Cleaning
- Feature Engineering
- Technical Feature Extraction
- Career Feature Extraction
- Candidate Metadata Generation
- Candidate Normalization

This module serves as the foundation for the entire TalentMindAI pipeline.

---

# Installation

```bash
cd project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

# Dataset

Supported candidate datasets:

```
candidates.json
candidates.jsonl
sample_candidates.json
```

Place datasets inside:

```
data/
```

---

# Candidate Processing Pipeline

```
Raw Candidate Dataset
        │
        ▼
Schema Validation
        │
        ▼
Missing Value Handling
        │
        ▼
Candidate Normalization
        │
        ▼
Feature Engineering
        │
        ▼
Technical Features
Career Features
Metadata
        │
        ▼
Clean Candidate Dataset
```

---

# Features Generated

## Technical Features

The module extracts technical capabilities including:
- Programming Languages
- Machine Learning
- Deep Learning
- LLM Experience
- Vector Database Experience
- Retrieval Systems
- Ranking Systems
- Backend Development
- Cloud Technologies
- Data Engineering

Example:
```
{
    "python_score":0.92,
    "llm_score":0.88,
    "retrieval_score":0.81,
    "backend_score":0.74
}
```

---

## Career Features

Extracted career intelligence:
- Years of Experience
- Leadership Experience
- Promotion Count
- Company Reputation
- Startup Experience
- Product Company Experience
- Industry
- Current Position

Example
```
{
    "experience_years":7,
    "leadership":True,
    "career_growth":0.83
}
```

---

## Candidate Metadata

Additional candidate information:
- Candidate ID
- Name
- Current Company
- Current Title
- Location
- Industry
- Skills
- Education

---

# Outputs

Generated files
```
clean_candidates.csv

candidate_metadata.csv

candidate_features_raw.csv
```

---

## candidate_features_raw.csv

Contains raw technical features used by downstream modules.

Example

| candidate_id | llm_score | retrieval_score | backend_score | career_growth |
|--------------|-----------|----------------|---------------|---------------|

---

## clean_candidates.csv

Normalized candidate information.

Contains:
- Skills
- Career History
- Education
- Profile Summary
- Experience

---

## candidate_metadata.csv

Contains lightweight metadata used by dashboard.

Fields:
```
candidate_id
candidate_name
location
current_title
current_company
experience_years
```

---

# Project Structure

```
project/
│

├── data/

├── candidate_metadata.csv

├── clean_candidates.csv

├── candidate_features_raw.csv

├── feature_engineering.py

├── candidate_loader.py

├── schema_validator.py

├── README.md
```

---

# Pipeline Usage

Run feature engineering

```bash
python feature_engineering.py
```

Validate schema

```bash
python schema_validator.py
```

Generate cleaned dataset

```bash
python candidate_loader.py
```

---

# Integration

This module provides the base dataset for all remaining project modules.

## Semantic Matching Pipeline

Consumes:

```
clean_candidates.csv
```

Uses:
- Skills
- Experience
- Profile Summary
- Career History

for Semantic Matching.

---

## Trust and Behavior Engine

Consumes:

```
candidate_features_raw.csv
```

Uses:

- Technical Signals
- Candidate Metadata

to compute:

- Behavior Score
- Availability Score
- Trust Score

---

## Ranking Engine and Dashboard

Consumes:

```
candidate_features_raw.csv

candidate_metadata.csv
```

Uses:

- Technical Scores
- Career Features
- Leadership
- Metadata

for Talent DNA Ranking.

---

# Design Principles

The feature engineering pipeline follows four principles.

## Data Consistency

Normalize all candidate records into a unified schema.

---

## Scalability

Optimized to process over **100,000 candidate profiles** efficiently.

---

## Reusability

Each downstream module uses the generated features independently.

---

## Explainability

Every engineered feature corresponds to an interpretable candidate characteristic.

---

# Generated Features

Technical Intelligence

- Python
- Machine Learning
- Deep Learning
- NLP
- LLM
- Retrieval
- Ranking
- Backend
- Cloud

Career Intelligence

- Experience
- Leadership
- Career Growth
- Promotions
- Company Type
- Industry

Metadata

- Candidate Information
- Company
- Location
- Education

---

# Team Integration

This module is the starting point of the TalentMindAI pipeline.

```
Raw Dataset
      │
      ▼
Feature Engineering
(Kanishq Joshi)
      │
      ├──────────────► Semantic Matching
      │                    (Soham Balsaraf)
      │
      ├──────────────► Behavior & Trust
      │                    (Om Karanje)
      │
      └──────────────► Ranking Engine
                           (Sharad Shinde)
```

---

# Performance

Optimized for

- 100,000+ Candidates
- Low Memory Usage
- CPU Execution
- Modular Integration

---

# Author

**Feature Engineer**

Role:

Feature Engineering & Candidate Intelligence

Project:

TalentMindAI — AI Powered Candidate Discovery & Ranking Platform

Redrob Intelligent Candidate Discovery & Ranking Challenge
