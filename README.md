<div align="center">

#  TalentMindAI

### AI-Powered Intelligent Candidate Discovery & Ranking Platform

An end-to-end AI Recruitment Intelligence System capable of ranking **100,000+ candidates** using **Semantic AI**, **Behavioral Intelligence**, **Trust Scoring**, and **Explainable AI**.

<img width="1983" height="793" alt="banner" src="https://github.com/user-attachments/assets/bd5cd37a-1f3a-4c42-909f-0865f29cd828" />



![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit)
![Sentence Transformers](https://img.shields.io/badge/Embeddings-bge--small--en--v1.5-green)
![Pandas](https://img.shields.io/badge/Data-Pandas-yellow)
![License](https://img.shields.io/badge/Hackathon-Redrob-orange)

</div>

#  Table of Contents

- Overview
- Features
- System Architecture
- AI Pipeline
- Project Structure
- Installation
- Running the Project
- Dashboard
- Outputs
- Team Contributions
- Future Scope

# Architecture Diagram

```mermaid
flowchart TD

A[Job Description]

A --> B[JD Intelligence Engine]

C[100K Candidate Dataset]

C --> D[Feature Engineering]

D --> E[Semantic Matching]

D --> F[Behavior Engine]

D --> G[Trust Engine]

E --> H[Talent DNA Ranker]

F --> H

G --> H

H --> I[Explainability Layer]

I --> J[Recruiter Dashboard]
```

# AI Pipeline

Candidates

↓

Feature Engineering

↓

Semantic Matching

↓

Behavior

↓

Trust

↓

Ranking

↓

Dashboard

# Dashboard Preview

## Dashboard

<img width="1600" height="746" alt="Dashboard" src="https://github.com/user-attachments/assets/b9360be3-bc8d-4662-857a-1fee9628e16e" />


---

## Rankings

<img width="1562" height="797" alt="Rankings" src="https://github.com/user-attachments/assets/a9693acd-4dc9-4a41-b987-17e6819dd8f8" />


---

## Candidate Insights

<img width="1572" height="927" alt="Candidate Insights" src="https://github.com/user-attachments/assets/fb416c2c-4ec3-44c1-8718-fff8418185ef" />


# Folder Structure

TalentMindAI/

├── app.py
├── ranker.py
├── reason_generator.py
├── integration_test.py
│
├── behavior_engine.py
├── trust_engine.py
├── generate_features.py
├── market_stats.py
│
├── run_matching.py
├── interactive_test.py
│
├── src/
├── data/
├── outputs/
├── notebooks/
│
├── requirements.txt
└── README.md

# Team Contribution

| Module              | Owner    |
| ------------------- | -------- |
| Feature Engineering | Kanishq Joshi |
| JD Intelligence     | Soham Balsaraf |
| Semantic Matching   | Soham Balsaraf |
| Behavior Engine     | Om Karanje |
| Trust Engine        | Om Karanje |
| Ranking Engine      | Sharad Shinde |
| Explainability      | Sharad Shinde |
| Dashboard           | Sharad Shinde |

# Tech Stack

| Category       | Technology            |
| -------------- | --------------------- |
|  Language      | Python                |
|  Data          | Pandas, NumPy         |
|  AI            | Sentence Transformers |
|  Visualization | Plotly                |
|  Frontend      | Streamlit             |
|  Storage       | JSON, CSV, JSONL      |

# Outputs

| File                        | Description               |
| --------------------------- | ------------------------- |
| candidate_features.csv      | Behavior & Trust features |
| semantic_features.json      | Semantic outputs          |
| top_candidates.csv          | Final ranked candidates   |
| parsed_jd.json              | Parsed Job Description    |
| jd_intelligence.json        | JD metadata               |
| candidate_explanations.json | Explainable AI            |

# Future Scope

Roadmap

✅ Semantic Matching

✅ Behavioral Intelligence

✅ Trust Engine

✅ Explainable AI

⬜ Resume PDF Upload

⬜ ATS Integration

⬜ AI Interview Assistant

⬜ Recruiter Copilot

⬜ LLM-powered Resume Parsing

⬜ Candidate Chatbot

⬜ Multi-language Support

---

<div align="center">

Built with ❤️ by Team TalentMindAI

Redrob Intelligent Candidate Discovery & Ranking Challenge

⭐ Star this repository if you found it useful!

</div>
