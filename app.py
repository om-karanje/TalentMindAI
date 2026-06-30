import os
import time
import json
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from ranker import run_ranker, BASE_DIR, extract_skills_from_jd
from reason_generator import generate_explanations

# Set page config for a widescreen layout with modern branding
st.set_page_config(
    page_title="TalentMindAI | Enterprise Recruiter Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RANKED_CSV = os.path.join(OUTPUT_DIR, "ranked_candidates.csv")
CLEAN_CSV = os.path.join(DATA_DIR, "candidate_features_raw.csv")
CAND_META_CSV = os.path.join(DATA_DIR, "behavior_scores.csv")
EXPLANATIONS_JSON = os.path.join(DATA_DIR, "candidate_explanations.json")

# Core Data Loaders - Utilizing file modification times to prevent cache bugs
@st.cache_data
def load_data(ranked_mtime, raw_mtime, beh_mtime):
    df = pd.read_csv(RANKED_CSV)
    df_raw = pd.read_csv(CLEAN_CSV)
    df_beh = pd.read_csv(CAND_META_CSV)
    
    # Merge clean titles/companies for visualization
    clean_cand_path = os.path.join(DATA_DIR, "candidate_features_raw.csv")
    if os.path.exists(os.path.join(DATA_DIR, "clean_candidates.csv")):
        clean_cand_path = os.path.join(DATA_DIR, "clean_candidates.csv")
    df_clean = pd.read_csv(clean_cand_path)
    
    # Defensive column population if missing from fallback file
    if 'current_title' not in df_clean.columns:
        df_clean['current_title'] = "AI Software Engineer"
    if 'current_company' not in df_clean.columns:
        df_clean['current_company'] = "Autonomous Corp"
    if 'skills_count' not in df_clean.columns:
        df_clean['skills_count'] = 10
    if 'notice_period' not in df_clean.columns:
        df_clean['notice_period'] = 60
        
    # Build merge columns dynamically - only merge columns not already in df
    desired_cols = ['skills_count', 'notice_period', 'saved_by_recruiters', 'response_rate', 'current_title', 'current_company']
    cols_to_merge = ['candidate_id']
    for col in desired_cols:
        if col not in df.columns and col in df_clean.columns:
            cols_to_merge.append(col)
        
    df_extended = pd.merge(df, df_clean[cols_to_merge], on='candidate_id', how='left')
    return df_extended, df_raw, df_beh

@st.cache_data
def load_explanations(expl_mtime):
    if os.path.exists(EXPLANATIONS_JSON):
        with open(EXPLANATIONS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {item['candidate_id']: item for item in data}
    return {}

# Load file modification times dynamically
ranked_mtime = os.path.getmtime(RANKED_CSV) if os.path.exists(RANKED_CSV) else 0
raw_mtime = os.path.getmtime(CLEAN_CSV) if os.path.exists(CLEAN_CSV) else 0
beh_mtime = os.path.getmtime(CAND_META_CSV) if os.path.exists(CAND_META_CSV) else 0
expl_mtime = os.path.getmtime(EXPLANATIONS_JSON) if os.path.exists(EXPLANATIONS_JSON) else 0

# Load datasets safely
try:
    df_ranked, df_raw_feats, df_behavior = load_data(ranked_mtime, raw_mtime, beh_mtime)
    explanations_map = load_explanations(expl_mtime)
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# Initialize session state keys
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True # Defaulting to Dark Mode for premium look
if "compare_list" not in st.session_state:
    st.session_state.compare_list = []
if "menu_selection" not in st.session_state:
    st.session_state.menu_selection = "Dashboard"
if "menu_key" not in st.session_state:
    st.session_state.menu_key = 0
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = df_ranked.iloc[0]['candidate_id'] if not df_ranked.empty else None

default_jd_text = """Founding AI Engineer - Search & Retrieval Systems
Required Skills:
- Python, Go, and Distributed Systems.
- Semantic Search, Embeddings, Sentence Transformers.
- Vector Databases (Milvus, Qdrant, Pinecone) and vector indexes.
- PEFT, model fine-tuning, and RAG architectures."""

if "jd_text" not in st.session_state:
    st.session_state.jd_text = default_jd_text

def navigate_to(page_name):
    st.session_state.menu_selection = page_name
    st.session_state.menu_key += 1
    st.rerun()

@st.cache_data
def load_metadata_dict():
    metadata_csv = os.path.join(DATA_DIR, "candidate_metadata.csv")
    if os.path.exists(metadata_csv):
        try:
            df_meta = pd.read_csv(metadata_csv)
            return dict(zip(df_meta['candidate_id'], zip(df_meta['anonymized_name'], df_meta['location'])))
        except Exception as e:
            print(f"Error reading candidate_metadata.csv: {e}")
    return {}

candidate_metadata = load_metadata_dict()

def get_candidate_meta(candidate_id):
    # Try to load actual candidate name/location from dataset metadata dict
    if candidate_id in candidate_metadata:
        return candidate_metadata[candidate_id]
        
    # Fallback deterministically if not found (e.g. for mock scenarios or integration tests)
    import hashlib
    NAMES = [
        "Sarah Jenkins", "Michael Chen", "Emily Rodriguez", "David Kim", "Jessica Taylor", 
        "James Smith", "Robert Johnson", "Patricia Williams", "John Doe", "Jane Miller", 
        "Aarav Patel", "Yusuf Al-Farsi", "Chloe Dubois", "Kenji Sato", "Sonia Kovalev", 
        "Carlos Santana", "Amara Diallo", "Oliver Thompson", "Elena Rostova", "Liam O'Connor"
    ]
    LOCATIONS = [
        "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Chicago, IL", 
        "Boston, MA", "Denver, CO", "Los Angeles, CA", "Toronto, ON", "London, UK"
    ]
    hash_object = hashlib.md5(candidate_id.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    hash_int = int(hash_hex, 16)
    name = NAMES[hash_int % len(NAMES)]
    location = LOCATIONS[(hash_int * 3) % len(LOCATIONS)]
    return name, location

# Theme CSS Configuration (Talent AI UI Design System: Recruiter Light Theme / Dark Mode toggle)
if st.session_state.dark_mode:
    bg_color = "#0B0C10"
    card_bg = "#13151D"
    text_color = "#F8FAFC"
    border_color = "rgba(255, 255, 255, 0.08)"
    shadow = "none"
    hover_border = "#4F46E5"
    sub_text = "#94A3B8"
    input_bg = "#191B24"
    metric_label = "#94A3B8"
    sidebar_bg = "#0D0E12"
    sidebar_text = "#F8FAFC"
else:
    bg_color = "#FAFBFD"
    card_bg = "#FFFFFF"
    text_color = "#1E293B"
    border_color = "#E2E8F0"
    shadow = "0 1px 3px rgba(0, 0, 0, 0.02)"
    hover_border = "#4F46E5"
    sub_text = "#64748B"
    input_bg = "#FFFFFF"
    metric_label = "#64748B"
    sidebar_bg = "#EEF2F6"
    sidebar_text = "#1E293B"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    .stApp {{
        background-color: {bg_color} !important;
    }}
    
    /* Scroll/Render Animation Framework */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .saas-animate-1 {{ animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both; }}
    .saas-animate-2 {{ animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both; }}
    .saas-animate-3 {{ animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both; }}
    .saas-animate-4 {{ animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both; }}
    
    /* Card Style matching screenshots */
    .saas-card {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: {shadow} !important;
        margin-bottom: 15px !important;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: {text_color} !important;
    }}
    .saas-card:hover {{
        transform: translateY(-2px) !important;
        border-color: {hover_border} !important;
    }}
    
    .saas-subtext {{
        color: {sub_text} !important;
        font-size: 0.85rem;
    }}
    
    .saas-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: {text_color} !important;
    }}
    
    /* Sidebar Layout Restyle to match Talent AI blue-grey theme */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_color} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {sidebar_text} !important;
    }}
    
    /* Badge Pill Styling */
    .badge-gold {{ background-color: rgba(245, 158, 11, 0.12); color: #D97706; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; border: 1px solid rgba(245, 158, 11, 0.2); }}
    .badge-silver {{ background-color: #E2E8F0; color: #4B5563; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; }}
    .badge-bronze {{ background-color: rgba(194, 65, 12, 0.12); color: #C2410C; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; }}
    .badge-primary {{ background-color: rgba(79, 70, 229, 0.12); color: #4F46E5; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; border: 1px solid rgba(79, 70, 229, 0.2); }}
    .badge-success {{ background-color: rgba(34, 197, 94, 0.12); color: #15803D; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; border: 1px solid rgba(34, 197, 94, 0.2); }}
    .badge-danger {{ background-color: rgba(239, 68, 68, 0.12); color: #B91C1C; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; border: 1px solid rgba(239, 68, 68, 0.2); }}
    .badge-warning {{ background-color: rgba(245, 158, 11, 0.12); color: #F59E0B; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; border: 1px solid rgba(245, 158, 11, 0.2); }}
    .badge-info {{ background-color: rgba(59, 130, 246, 0.12); color: #2563EB; font-weight: 600; border-radius: 6px; padding: 4px 10px; display: inline-block; font-size: 0.75rem; border: 1px solid rgba(59, 130, 246, 0.2); }}
    
    /* Strengths and Risks styling */
    .strength-box {{
        background: rgba(34, 197, 94, 0.05);
        border-left: 4px solid #22C55E;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: {text_color};
        animation: fadeInUp 0.4s ease-out;
    }}
    .risk-box {{
        background: rgba(239, 68, 68, 0.05);
        border-left: 4px solid #EF4444;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: {text_color};
        animation: fadeInUp 0.4s ease-out;
    }}
    .recommendation-box {{
        background: rgba(79, 70, 229, 0.05);
        border-left: 4px solid #4F46E5;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: {text_color};
        animation: fadeInUp 0.4s ease-out;
    }}
    
    .saas-divider {{
        height: 1px;
        background-color: {border_color};
        margin: 20px 0;
    }}
</style>
""", unsafe_allow_html=True)

# Navigation Menu Options
pages = ["Dashboard", "Upload", "Rankings", "Insights", "Analytics", "Settings"]

# Set default page navigation index
if "menu_selection" in st.session_state:
    try:
        default_index = pages.index(st.session_state.menu_selection)
    except ValueError:
        default_index = 0
else:
    default_index = 0

# Render Custom Sidebar Navigation (with branding logo and bottom profile card)
with st.sidebar:
    st.markdown(f"""
    <div style='padding: 15px 0 25px 0;'>
        <h2 style='color: #4F46E5; font-family: Poppins, sans-serif; margin: 0; font-weight: 700; font-size: 1.6rem;'>TalentMindAI</h2>
        <span style='color: #64748B; font-size: 0.85rem; font-weight: 500;'>Enterprise Recruiter</span>
    </div>
    <div style='height: 1px; background-color: {border_color}; margin-bottom: 20px;'></div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 10px; padding: 15px; margin-bottom: 20px;'>
        <span style='color: {sub_text}; font-size: 0.75rem;'>Active Job Posting</span><br>
        <strong style='font-size: 0.9rem; color: {text_color};'>Senior Full-Stack Architect</strong>
        <div style='display: flex; gap: 8px; margin-top: 8px;'>
            <span class='badge-primary'>Active</span>
            <span class='badge-info'>12 Candidates</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bottom Profile Card
    st.markdown(f"""
    <div style='height: 250px;'></div>
    <div style='height: 1px; background-color: {border_color}; margin: 20px 0;'></div>
    <div style='display: flex; align-items: center; gap: 12px;'>
        <div style='width: 40px; height: 40px; border-radius: 50%; background-color: #E2E8F0; display: flex; align-items: center; justify-content: center; overflow: hidden;'>
            <svg viewBox="0 0 100 100" style="width: 40px; height: 40px; margin-top: 6px;">
                <circle cx="50" cy="35" r="18" fill="#94A3B8" />
                <path d="M15,82 C15,65 30,55 50,55 C70,55 85,65 85,82" fill="#94A3B8" />
            </svg>
        </div>
        <div>
            <strong style='color: {text_color}; font-size: 0.9rem;'>Aarav Patel</strong><br>
            <span style='color: {sub_text}; font-size: 0.75rem;'>Recruitment Lead</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Container Header Top Bar (Brand/Search + Horizontal Navigation + icons)
nav_c1, nav_c2 = st.columns([1.5, 3.5])
with nav_c1:
    st.markdown(f"""
    <div style='padding-top: 5px;'>
        <strong style='font-family: Poppins, sans-serif; font-size: 1.4rem; color: #4F46E5;'>TalentMindAI</strong>
    </div>
    """, unsafe_allow_html=True)
with nav_c2:
    selected_page = option_menu(
        None,
        pages,
        icons=["grid-1x2", "cloud-upload", "people", "brain", "bar-chart-line", "gear"],
        default_index=default_index,
        orientation="horizontal",
        key=f"menu_widget_{st.session_state.menu_key}",
        styles={
            "container": {"background-color": sidebar_bg, "padding": "0px", "border": f"1px solid {border_color}", "border-radius": "8px"},
            "icon": {"color": "#64748B", "font-size": "14px"}, 
            "nav-link": {"font-size": "13px", "text-align": "center", "margin":"0px", "color": text_color, "font-family": "Inter, sans-serif"},
            "nav-link-selected": {"background-color": "#4F46E5", "color": "white", "font-weight": "600"},
        }
    )
    st.session_state.menu_selection = selected_page

st.markdown(f"<div style='height: 1px; background-color: {border_color}; margin: 15px 0 20px 0;'></div>", unsafe_allow_html=True)


# ----------------- PAGE 1: DASHBOARD (LANDING HERO) -----------------
if st.session_state.menu_selection == "Dashboard":
    
    # Large Purple Hero Ingest Banner
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%); padding: 35px; border-radius: 16px; color: white; margin-bottom: 20px;' class='saas-animate-1'>
        <h1 style='margin: 0; font-family: Poppins, sans-serif; font-size: 2.2rem; font-weight: 700; color: white;'>AI Candidate Ranking Dashboard</h1>
        <p style='margin: 15px 0 25px 0; font-size: 1.05rem; opacity: 0.9; max-width: 700px; line-height: 1.5; color: white;'>
            Upload a Job Description and instantly discover the best candidates using Semantic AI and Talent DNA.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Buttons overlayed under the purple banner
    btn_c1, btn_c2, btn_empty = st.columns([1, 1, 2])
    with btn_c1:
        if st.button("📄 Upload Job Description", key="hero_upload_btn", use_container_width=True, type="primary"):
            navigate_to("Upload")
    with btn_c2:
        if st.button("👁️ View Rankings", key="hero_view_btn", use_container_width=True):
            navigate_to("Rankings")
            
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # 5 Performance Stats Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown("""
        <div class='saas-card saas-animate-1'>
            <span class='saas-subtext'>Total Candidates</span>
            <h3 style='margin: 5px 0; font-size: 1.6rem; font-family: Poppins, sans-serif;'>12,482</h3>
            <span style='color: #22C55E; font-size: 0.8rem; font-weight: 600;'>📈 +14% this month</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class='saas-card saas-animate-2'>
            <span class='saas-subtext'>Ranked Candidates</span>
            <h3 style='margin: 5px 0; font-size: 1.6rem; font-family: Poppins, sans-serif;'>8,910</h3>
            <span style='color: #64748B; font-size: 0.8rem;'>71.4% Coverage</span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class='saas-card saas-animate-3' style='border-left: 4px solid #4F46E5;'>
            <span class='saas-subtext' style='color:#4F46E5; font-weight: 500;'>Avg Talent DNA</span>
            <h3 style='margin: 5px 0; font-size: 1.6rem; color: #4F46E5; font-family: Poppins, sans-serif;'>84.2%</h3>
            <span style='color: #4F46E5; font-size: 0.8rem; font-weight: 600;'>Enterprise Grade</span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class='saas-card saas-animate-4'>
            <span class='saas-subtext'>Best Match</span>
            <h3 style='margin: 5px 0; font-size: 1.6rem; font-family: Poppins, sans-serif;'>98.1%</h3>
            <span style='color: #64748B; font-size: 0.8rem;'>Product Designer</span>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown("""
        <div class='saas-card saas-animate-1'>
            <span class='saas-subtext'>Processing Time</span>
            <h3 style='margin: 5px 0; font-size: 1.6rem; font-family: Poppins, sans-serif;'>1.2s</h3>
            <span style='color: #64748B; font-size: 0.8rem;'>Real-time AI logic</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Recent Rankings Table (matches Image 1 style)
    st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
        <h3 style='margin: 0; font-family: Poppins, sans-serif; font-size: 1.3rem; font-weight: 600;'>Recent Rankings</h3>
        <a href='#' style='color: #4F46E5; font-weight: 600; text-decoration: none; font-size: 0.9rem;'>View All</a>
    </div>
    """, unsafe_allow_html=True)
    
    for idx, row in df_ranked.head(3).iterrows():
        name, location = get_candidate_meta(row['candidate_id'])
        status_text = "INTERVIEWING" if idx % 2 == 0 else "SCREENING"
        status_class = "badge-success" if idx % 2 == 0 else "badge-info"
        match_pct = int(row['talent_dna'] * 100)
        
        st.markdown(f"""
        <div class='saas-card saas-animate-2' style='display: flex; align-items: center; justify-content: space-between; padding: 15px 24px; margin-bottom: 12px;'>
            <div style='display: flex; align-items: center; gap: 15px; width: 30%;'>
                <div style='width: 38px; height: 38px; border-radius: 50%; background-color: #EEF2FF; color: #4F46E5; display: flex; justify-content: center; align-items: center; font-weight: 600; font-size: 1.05rem;'>
                    {name[0]}
                </div>
                <div>
                    <strong style='font-size: 0.95rem; color:{text_color};'>{name}</strong><br>
                    <span style='color: #64748B; font-size: 0.78rem;'>{row.get('current_title', 'AI Engineer')}</span>
                </div>
            </div>
            <div style='width: 30%; display: flex; align-items: center; gap: 10px;'>
                <span style='font-size: 0.85rem; color: #64748B;'>Role Match:</span>
                <div style='width: 120px; height: 6px; background-color: #E2E8F0; border-radius: 3px; position: relative;'>
                    <div style='width: {match_pct}%; height: 100%; background-color: #4F46E5; border-radius: 3px;'></div>
                </div>
                <strong style='font-size: 0.85rem; color:{text_color};'>{match_pct}%</strong>
            </div>
            <div style='width: 20%;'>
                <span class='badge-primary'>A+ Elite</span>
            </div>
            <div style='width: 20%; text-align: right;'>
                <span class='{status_class}'>{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- PAGE 2: UPLOAD -----------------
elif st.session_state.menu_selection == "Upload":
    st.markdown("<h2 class='saas-title'>Ingest Job Description</h2>", unsafe_allow_html=True)
    st.markdown("<p class='saas-subtext'>Upload the JD file to extract requirements, classify must-haves, and trigger semantic pipeline mapping.</p>", unsafe_allow_html=True)
    
    col_uploader, col_intel = st.columns([1, 1])
    
    with col_uploader:
        with st.container(border=True):
            st.markdown("#### Paste Job Description")
            
            jd_text = st.text_area("Job Description Details:", value=st.session_state.jd_text, height=220)
            st.session_state.jd_text = jd_text
            
            trigger_ranking = st.button("🚀 Trigger AI Ranking Pipeline", use_container_width=True, type="primary", key="run_pipeline_btn")
            
        if trigger_ranking:
            # Validation 1: Empty Check
            if not jd_text.strip():
                st.error("❌ Job Description cannot be empty! Please paste requirements.")
            else:
                # Validation 2: Skill matching check
                extracted_skills = list(extract_skills_from_jd(jd_text))
                if not extracted_skills:
                    st.error("❌ Invalid Job Description! No core technical skills recognized (e.g. Python, Go, SQL, LLM, NLP, Vector DB, PEFT, etc.). Please add some technical requirements.")
                else:
                    # 1. Save pasted JD text
                    pasted_jd_path = os.path.join(DATA_DIR, "pasted_jd.txt")
                    with open(pasted_jd_path, "w", encoding="utf-8") as f:
                        f.write(jd_text)
                        
                    # 2. Generate and write parsed_jd.json dynamically
                    try:
                        # Classify Domain
                        jd_lower = jd_text.lower()
                        domain = "AI Engineering"
                        if "search" in jd_lower or "retrieval" in jd_lower:
                            domain = "AI Search"
                        elif "nlp" in jd_lower or "language" in jd_lower or "transformer" in jd_lower:
                            domain = "NLP/LLM"
                        
                        # Classify Seniority
                        seniority = "Senior/Founding"
                        if "lead" in jd_lower or "principal" in jd_lower:
                            seniority = "Lead/Principal"
                        elif "junior" in jd_lower or "intern" in jd_lower:
                            seniority = "Junior"
                        
                        # Dynamic metadata structure matching Person 2
                        parsed_jd_data = {
                            "domain": domain,
                            "experience": 4.0 if "senior" in jd_lower or "lead" in jd_lower else 2.0,
                            "seniority": seniority,
                            "must_have": extracted_skills
                        }
                        
                        parsed_jd_path = os.path.join(DATA_DIR, "parsed_jd.json")
                        with open(parsed_jd_path, "w", encoding="utf-8") as f:
                            json.dump(parsed_jd_data, f, indent=2)
                    except Exception as e:
                        print(f"Error parsing job description: {e}")

                    # Simulated progress bar
                    progress_bar = st.progress(0)
                    status = st.empty()
                    
                    steps = [
                        ("Extracting JD requirements and must-have skills...", 0.15),
                        ("Interfacing with Person 1 (Feature engineering parquet ingestion)...", 0.35),
                        ("Integrating Person 2 Semantic scores...", 0.55),
                        ("Merging Person 3 Behavior & Trust engine data...", 0.75),
                        ("Calculating Technical Fit & Talent DNA indexes...", 0.90),
                        ("Candidate database ranked successfully!", 1.0)
                    ]
                    
                    for step, pct in steps:
                        status.markdown(f"<p style='color:#4F46E5; font-weight:600;'>{step}</p>", unsafe_allow_html=True)
                        progress_bar.progress(pct)
                        time.sleep(0.4)
                        
                    run_ranker(DATA_DIR, OUTPUT_DIR)
                    load_data.clear() # Explicitly invalidate Streamlit's read cache
                    st.success("Pipeline processing complete! Candidate database successfully indexed.")
                    time.sleep(1.0)
                    st.rerun()
            
    with col_intel:
        # Load sample parsed jd intelligence
        parsed_jd_path = os.path.join(DATA_DIR, "parsed_jd.json")
        if os.path.exists(parsed_jd_path):
            with open(parsed_jd_path, 'r', encoding='utf-8') as f:
                jd_intel = json.load(f)
            
            with st.container(border=True):
                st.markdown("<div class='saas-animate-2'>", unsafe_allow_html=True)
                st.markdown("#### parsed Job Description Intel")
                st.markdown(f"<strong>Domain Classification:</strong> <span class='badge-info'>{jd_intel.get('domain', 'AI Search').upper()}</span>", unsafe_allow_html=True)
                st.markdown(f"<strong>Required Experience:</strong> <code>{jd_intel.get('experience', 3.5)} years</code>", unsafe_allow_html=True)
                st.markdown(f"<strong>Target Seniority:</strong> <code>{jd_intel.get('seniority', 'Senior/Founding')}</code>", unsafe_allow_html=True)
                
                st.markdown("**Must Have Core Skills:**")
                skills = jd_intel.get("must_have", [])
                skills_html = "".join([f"<span class='badge-primary' style='margin: 4px;'>{s}</span>" for s in skills])
                st.markdown(f"<div style='margin-bottom:15px;'>{skills_html}</div>", unsafe_allow_html=True)
                
                st.markdown("**Nice To Have Skills:**")
                nice_to_have = ["Golang", "PEFT fine-tuning", "Milvus", "Distributed Systems"]
                nice_html = "".join([f"<span class='badge-info' style='margin: 4px;'>{s}</span>" for s in nice_to_have])
                st.markdown(nice_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No parsed JD metadata available. Upload or trigger the ranking pipeline to parse JD details.")

# ----------------- PAGE 3: RANKINGS (WITH TOP 3 FEATURED CARDS) -----------------
elif st.session_state.menu_selection == "Rankings":
    st.markdown("<h2 class='saas-title saas-animate-1'>Candidate Rankings</h2>", unsafe_allow_html=True)
    st.markdown("<p class='saas-subtext saas-animate-2'>Top matches mapped and rank-ordered against JD criteria.</p>", unsafe_allow_html=True)
    
    # Filter controls row
    filter_c1, filter_c2, filter_c3, filter_c4 = st.columns([1.5, 1.2, 1.2, 1.1])
    with filter_c1:
        only_top_semantic = st.checkbox("Show Top Semantic Matches Only", value=False)
    with filter_c2:
        sort_by = st.selectbox("Sort By:", ["Overall Score", "Talent DNA Score", "Semantic Match Score", "Behavior Score", "Technical Fit"])
    with filter_c3:
        display_limit = st.slider("Display Limit:", min_value=5, max_value=100, value=15, step=5)
    with filter_c4:
        layout_mode = st.radio("Layout Mode:", ["Data Table", "Grid Cards"], index=0, horizontal=True)
        
    filtered_df = df_ranked.copy()
    if only_top_semantic:
        filtered_df = filtered_df[filtered_df['semantic_score'] > 0.0]
        
    # Sort
    if sort_by == "Overall Score":
        filtered_df = filtered_df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
    elif sort_by == "Talent DNA Score":
        filtered_df = filtered_df.sort_values(by="talent_dna", ascending=False).reset_index(drop=True)
    elif sort_by == "Semantic Match Score":
        filtered_df = filtered_df.sort_values(by="semantic_score", ascending=False).reset_index(drop=True)
    elif sort_by == "Behavior Score":
        filtered_df = filtered_df.sort_values(by="behavior_score", ascending=False).reset_index(drop=True)
    elif sort_by == "Technical Fit":
        filtered_df = filtered_df.sort_values(by="technical_fit", ascending=False).reset_index(drop=True)
        
    filtered_df['rank'] = filtered_df.index + 1
    display_df = filtered_df.head(display_limit)
    
    # Render Top 3 Featured Candidates Grid (Image 2 style)
    r1_row = filtered_df.iloc[0] if len(filtered_df) > 0 else None
    r2_row = filtered_df.iloc[1] if len(filtered_df) > 1 else r1_row
    r3_row = filtered_df.iloc[2] if len(filtered_df) > 2 else r1_row
    
    if r1_row is not None:
        col_r2, col_r1, col_r3 = st.columns([1, 1.1, 1])
        
        with col_r2:
            r2_name, _ = get_candidate_meta(r2_row['candidate_id'])
            st.markdown(f"""
            <div class='saas-card saas-animate-1' style='text-align: center; border-color: {border_color}; padding: 20px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='width: 24px; height: 24px; border-radius: 50%; background-color: #E2E8F0; display: inline-flex; justify-content: center; align-items: center; font-weight: bold; font-size: 0.85rem; color: #1E293B;'>2</span>
                    <strong style='color:#4F46E5;'>{r2_row['talent_dna']:.1%}</strong>
                </div>
                <h4 style='margin: 15px 0 5px 0;'>{r2_name}</h4>
                <p style='color:{sub_text}; font-size:0.8rem; margin-bottom: 15px;'>{r2_row.get('current_title', 'Developer')}</p>
                <div style='border-top:1px solid {border_color}; padding-top:10px; text-align: left;'>
                    <span style='font-size:0.75rem; color:{sub_text};'>Technical Fit</span>
                    <div style='width: 100%; height: 5px; background-color: #E2E8F0; border-radius: 2px; position: relative; margin-top: 4px;'>
                        <div style='width: {int(r2_row["technical_fit"]*100)}%; height: 100%; background-color: #4F46E5; border-radius: 2px;'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Analysis", key="featured_r2_btn", use_container_width=True):
                st.session_state.selected_candidate_id = r2_row['candidate_id']
                navigate_to("Insights")
            
        with col_r1:
            r1_name, _ = get_candidate_meta(r1_row['candidate_id'])
            st.markdown(f"""
            <div class='saas-card saas-animate-2' style='text-align: center; border: 2px solid #4F46E5; background-color: rgba(79, 70, 229, 0.01); padding: 25px; transform: scale(1.03);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='width: 30px; height: 30px; border-radius: 50%; background-color: #FCD34D; display: inline-flex; justify-content: center; align-items: center; font-weight: bold; font-size: 0.95rem; color: #1E293B;'>1</span>
                    <strong style='color:#4F46E5; font-size: 1.15rem;'>{r1_row['talent_dna']:.1%}</strong>
                </div>
                <h3 style='margin: 15px 0 5px 0; color:#4F46E5;'>{r1_name}</h3>
                <p style='color:{sub_text}; font-size:0.85rem; margin-bottom: 15px;'>{r1_row.get('current_title', 'Lead Architect')}</p>
                <div style='border-top:1px solid rgba(79, 70, 229, 0.15); padding-top:10px; text-align: left;'>
                    <span style='font-size:0.75rem; color:{sub_text};'>Semantic Relevance</span>
                    <div style='width: 100%; height: 5px; background-color: #E2E8F0; border-radius: 2px; position: relative; margin-top: 4px;'>
                        <div style='width: {int(r1_row["semantic_score"]*100)}%; height: 100%; background-color: #4F46E5; border-radius: 2px;'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Analysis", key="featured_r1_btn", use_container_width=True, type="primary"):
                st.session_state.selected_candidate_id = r1_row['candidate_id']
                navigate_to("Insights")
            
        with col_r3:
            r3_name, _ = get_candidate_meta(r3_row['candidate_id'])
            st.markdown(f"""
            <div class='saas-card saas-animate-3' style='text-align: center; border-color: {border_color}; padding: 20px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='width: 24px; height: 24px; border-radius: 50%; background-color: #FFEDD5; display: inline-flex; justify-content: center; align-items: center; font-weight: bold; font-size: 0.85rem; color: #C2410C;'>3</span>
                    <strong style='color:#4F46E5;'>{r3_row['talent_dna']:.1%}</strong>
                </div>
                <h4 style='margin: 15px 0 5px 0;'>{r3_name}</h4>
                <p style='color:{sub_text}; font-size:0.8rem; margin-bottom: 15px;'>{r3_row.get('current_title', 'Engineer')}</p>
                <div style='border-top:1px solid {border_color}; padding-top:10px; text-align: left;'>
                    <span style='font-size:0.75rem; color:{sub_text};'>Behavioral Match</span>
                    <div style='width: 100%; height: 5px; background-color: #E2E8F0; border-radius: 2px; position: relative; margin-top: 4px;'>
                        <div style='width: {int(r3_row["behavior_score"]*100)}%; height: 100%; background-color: #4F46E5; border-radius: 2px;'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Analysis", key="featured_r3_btn", use_container_width=True):
                st.session_state.selected_candidate_id = r3_row['candidate_id']
                navigate_to("Insights")
                
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    if layout_mode == "Grid Cards":
        st.markdown("#### Candidate Grid View")
        cols_per_row = 3
        for i in range(0, len(display_df), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(display_df):
                    row = display_df.iloc[i + j]
                    name, location = get_candidate_meta(row['candidate_id'])
                    match_pct = int(row['talent_dna'] * 100)
                    with cols[j]:
                        st.markdown(f"""
                        <div class='saas-card saas-animate-{((i//cols_per_row)+j)%4 + 1}' style='margin-bottom: 20px; position: relative;'>
                            <div style='position: absolute; top: 12px; right: 12px;'>
                                <span class='badge-primary'>#{row['rank']}</span>
                            </div>
                            <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 12px;'>
                                <div style='width: 38px; height: 38px; border-radius: 50%; background-color: #EEF2FF; color: #4F46E5; display: flex; justify-content: center; align-items: center; font-weight: 600;'>
                                    {name[0]}
                                </div>
                                <div>
                                    <strong style='font-size: 0.95rem; color: {text_color};'>{name}</strong><br>
                                    <span style='color: #64748B; font-size: 0.75rem;'>{row.get('current_title', 'AI Engineer')}</span>
                                </div>
                            </div>
                            <div style='margin-bottom: 12px; font-size: 0.85rem; color: {text_color};'>
                                📍 {location}<br>
                                💼 {row.get('years_experience', 0):.1f} yrs experience
                            </div>
                            <div style='margin-bottom: 12px;'>
                                <div style='display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;'>
                                    <span style='color: #64748B;'>Talent DNA:</span>
                                    <strong style='color: {text_color};'>{match_pct}%</strong>
                                </div>
                                <div style='width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 3px; position: relative;'>
                                    <div style='width: {match_pct}%; height: 100%; background-color: #4F46E5; border-radius: 3px;'></div>
                                </div>
                            </div>
                            <div style='display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 10px; margin-top: 10px;'>
                                <span>Tech: {int(row['technical_fit']*100)}%</span>
                                <span>Semantic: {int(row['semantic_score']*100)}%</span>
                                <span>Behavior: {int(row['behavior_score']*100)}%</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("View Analysis", key=f"grid_view_{row['candidate_id']}", use_container_width=True):
                            st.session_state.selected_candidate_id = row['candidate_id']
                            navigate_to("Insights")
    else:
        st.markdown("#### Candidate Ingestion list")
        display_cols = ['rank', 'candidate_id', 'current_title', 'years_experience', 'technical_fit', 'semantic_score', 'behavior_score', 'talent_dna', 'honeypot_penalty', 'final_score']
        formatter_df = display_df[display_cols].copy()
        
        mock_names = []
        for idx, row in formatter_df.iterrows():
            c_name, _ = get_candidate_meta(row['candidate_id'])
            mock_names.append(c_name)
        formatter_df.insert(2, 'candidate_name', mock_names)
        
        formatter_df['technical_fit'] = formatter_df['technical_fit'].map('{:.1%}'.format)
        formatter_df['semantic_score'] = formatter_df['semantic_score'].map('{:.1%}'.format)
        formatter_df['behavior_score'] = formatter_df['behavior_score'].map('{:.1%}'.format)
        formatter_df['talent_dna'] = formatter_df['talent_dna'].map('{:.1%}'.format)
        formatter_df['final_score'] = formatter_df['final_score'].map('{:.2f}'.format)
        
        st.dataframe(formatter_df, use_container_width=True, hide_index=True)
    
    # Export CSV action
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Full Ranked CSV List",
        data=csv_data,
        file_name="TalentMindAI_rankings.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_csv_btn"
    )

# ----------------- PAGE 4: INSIGHTS (CANDIDATE DETAIL DEEP DIVE) -----------------
elif st.session_state.menu_selection == "Insights":
    st.markdown("<h2 class='saas-title saas-animate-1'>Candidate DNA Deep Dive</h2>", unsafe_allow_html=True)
    st.markdown("<p class='saas-subtext saas-animate-2'>Detailed analysis of technical fit, semantic relevance, behavioral match, and credentials verification.</p>", unsafe_allow_html=True)
    
    # Candidate Selector
    top_candidates = df_ranked.head(100)['candidate_id'].tolist()
    
    # Ensure selected_candidate_id is valid
    if st.session_state.selected_candidate_id not in top_candidates:
        st.session_state.selected_candidate_id = top_candidates[0] if top_candidates else None
    
    def on_candidate_change():
        st.session_state.selected_candidate_id = st.session_state._insights_selector
    
    col_sel, col_empty = st.columns([2, 2])
    with col_sel:
        selected_cand_id = st.selectbox(
            "Select Candidate to Investigate:",
            top_candidates,
            index=top_candidates.index(st.session_state.selected_candidate_id),
            key="_insights_selector",
            on_change=on_candidate_change
        )
        
    cand_row = df_ranked[df_ranked['candidate_id'] == st.session_state.selected_candidate_id].iloc[0]
    name, location = get_candidate_meta(st.session_state.selected_candidate_id)
    
    st.markdown("<div class='saas-divider'></div>", unsafe_allow_html=True)
    
    # Layout Grid: Left column (photo/CV summary, Strengths box), Right column (Radar chart, circular indicator meters, experience history)
    detail_c1, detail_c2 = st.columns([1, 1.8])
    
    with detail_c1:
        # Profile Summary card (matches Image 3 style)
        with st.container(border=True):
            st.markdown(f"""
            <div style='text-align: center;' class='saas-animate-1'>
                <div style='width: 85px; height: 85px; border-radius: 50%; background-color: #EEF2FF; color: #4F46E5; display: inline-flex; justify-content: center; align-items: center; font-weight: 700; font-size: 2rem; margin-bottom: 15px; border: 2px solid #4F46E5;'>
                    {name[0]}
                </div>
                <div style='display: flex; justify-content: center; align-items: center; gap: 8px;'>
                    <h3 style='margin: 0; font-family: Poppins, sans-serif;'>{name}</h3>
                    <span class='badge-success' style='font-size: 0.75rem; padding: 2px 6px;'>Actively Looking</span>
                </div>
                <p style='color:#4F46E5; font-weight: 600; margin-top: 5px; margin-bottom: 2px;'>{cand_row.get('current_title', 'AI Architect')}</p>
                <span style='color:#64748B; font-size:0.85rem;'>📍 {location} (Remote)</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            # View CV and Portfolio buttons removed
                
        # Why This Candidate Ranked #1 Card (matches Image 3 style)
        with st.container(border=True):
            st.markdown(f"""
            <div style='background-color: rgba(79, 70, 229, 0.02); border-radius: 12px; padding: 15px;' class='saas-animate-2'>
                <h4 style='color: #4F46E5; margin-top: 0;'>⭐ Why This Candidate Ranked #{cand_row['rank']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            explanations = generate_explanations(cand_row)
            st.markdown("**Key Strengths**")
            if explanations["strengths"]:
                for strg in explanations["strengths"][:3]:
                    st.markdown(f"<div class='strength-box' style='padding: 8px 12px; font-size: 0.85rem;'>✓ {strg}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color: #64748B; font-size: 0.85rem; padding: 8px 12px;'>No notable strengths identified for this candidate.</div>", unsafe_allow_html=True)
                
            st.markdown("**Potential Risks**")
            if explanations["risks"]:
                for rsk in explanations["risks"][:2]:
                    st.markdown(f"<div class='risk-box' style='padding: 8px 12px; font-size: 0.85rem;'>⚠ {rsk}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color: #22C55E; font-size: 0.85rem; padding: 8px 12px;'>✓ No significant risks detected.</div>", unsafe_allow_html=True)
            
    with detail_c2:
        # Radar & Score card (matches Image 3 style)
        with st.container(border=True):
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;' class='saas-animate-1'>
                <h4 style='margin: 0; font-family: Poppins, sans-serif;'>Talent DNA Score</h4>
                <div style='text-align: right;'>
                    <span style='font-size: 2.2rem; font-weight: 800; color: #4F46E5;'>{int(cand_row['talent_dna']*100)}</span>
                    <span style='color: #64748B; font-weight: 600;'>/100</span><br>
                    <span style='color: #22C55E; font-size: 0.8rem; font-weight: 600;'>📈 Top 1% Match</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Radar chart
            categories = ['Technical Fit', 'Semantic Match', 'Behavior Index', 'Career Growth', 'Leadership', 'Availability', 'Trust Score']
            values = [
                cand_row['technical_fit'],
                cand_row['semantic_score'],
                cand_row['behavior_score'],
                cand_row['career_growth'],
                cand_row['leadership_score'],
                cand_row['availability_score'],
                cand_row['trust_score']
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                fillcolor='rgba(79, 70, 229, 0.08)',
                line=dict(color='#4F46E5', width=2)
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color=text_color,
                margin=dict(l=40, r=40, t=20, b=20),
                height=260
            )
            st.plotly_chart(fig, use_container_width=True, key=f"radar_{selected_cand_id}")
            
        # Bottom 4 circular indicators / columns (matches Image 3 style)
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center;' class='saas-animate-1'><h3 style='margin: 0; color: #4F46E5;'>{int(cand_row['technical_fit']*100)}</h3><small style='font-size:0.75rem; color:#64748B;'>Technical</small></div>", unsafe_allow_html=True)
        with rc2:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center;' class='saas-animate-2'><h3 style='margin: 0; color: #4F46E5;'>{int(cand_row['semantic_score']*100)}</h3><small style='font-size:0.75rem; color:#64748B;'>Semantic</small></div>", unsafe_allow_html=True)
        with rc3:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center;' class='saas-animate-3'><h3 style='margin: 0; color: #4F46E5;'>{int(cand_row['behavior_score']*100)}</h3><small style='font-size:0.75rem; color:#64748B;'>Behavioral</small></div>", unsafe_allow_html=True)
        with rc4:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center;' class='saas-animate-4'><h3 style='margin: 0; color: #4F46E5;'>{int(cand_row['trust_score']*100)}</h3><small style='font-size:0.75rem; color:#64748B;'>Reliability</small></div>", unsafe_allow_html=True)
                
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Professional Experience Timeline
        with st.container(border=True):
            st.markdown("#### Experience History")
            timeline_html = f"""
            <div style='border-left: 2px solid #E2E8F0; padding-left: 20px; margin-left: 10px; margin-top: 15px;' class='saas-animate-3'>
                <div style='position: relative; margin-bottom: 25px;'>
                    <div style='position: absolute; left: -26px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: #4F46E5;'></div>
                    <strong>{cand_row.get('current_title', 'AI Software Engineer')}</strong> at {cand_row.get('current_company', 'Autonomous Corp')} (2024 - Present)<br>
                    <span style='color: #64748B; font-size: 0.85rem;'>Led vector search architecture development and sentence embeddings indexing.</span>
                </div>
                <div style='position: relative; margin-bottom: 10px;'>
                    <div style='position: absolute; left: -26px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: #94A3B8;'></div>
                    <strong>Machine Learning Engineer</strong> at NextGen Analytics (2021 - 2024)<br>
                    <span style='color: #64748B; font-size: 0.85rem;'>Designed and deployed retrieval evaluation frameworks and LLM tuning loops.</span>
                </div>
            </div>
            """
            st.markdown(timeline_html, unsafe_allow_html=True)

# ----------------- PAGE 5: ANALYTICS -----------------
elif st.session_state.menu_selection == "Analytics":
    st.markdown("<h2 class='saas-title saas-animate-1'>Engine Analytics</h2>", unsafe_allow_html=True)
    st.markdown("<p class='saas-subtext saas-animate-2'>Analyze candidate scores, experience ranges, and key technical capabilities across the entire database.</p>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns([1, 1])
    plotly_template = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
    
    with col_chart1:
        with st.container(border=True):
            st.markdown("#### Talent DNA Score Distribution")
            fig = px.histogram(
                df_ranked, 
                x="talent_dna",
                nbins=30,
                color_discrete_sequence=["#4F46E5"],
                labels={"talent_dna": "Talent DNA Index"},
                height=300
            )
            fig.update_layout(
                template=plotly_template,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color=text_color,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with col_chart2:
        with st.container(border=True):
            st.markdown("#### Technical Fit vs Talent DNA")
            fig = px.scatter(
                df_ranked.head(100), 
                x="technical_fit", 
                y="talent_dna",
                size="years_experience", 
                color="final_score",
                color_continuous_scale="Viridis",
                labels={"technical_fit": "Technical Fit Score", "talent_dna": "Talent DNA Score"},
                height=300
            )
            fig.update_layout(
                template=plotly_template,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color=text_color,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

# ----------------- PAGE 6: SETTINGS -----------------
elif st.session_state.menu_selection == "Settings":
    st.markdown("<h2 class='saas-title saas-animate-1'>Settings</h2>", unsafe_allow_html=True)
    st.markdown("<p class='saas-subtext saas-animate-2'>Configure general theme parameters, adjust pipeline matching scoring weights, and perform database tasks.</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("#### SaaS Theme Adjustments")
        st.write("Toggle the theme state for the TalentMindAI UI dashboard.")
        
        # Dark / Light Mode Toggle Simulator
        dark_mode_active = st.checkbox("Enable Premium Dark Navy Theme", value=st.session_state.dark_mode)
        if dark_mode_active != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode_active
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("#### System Database Audits")
        st.write("Perform administrative database re-indexing tasks.")
        
        if st.button("Refresh Candidates Database", use_container_width=True, key="clear_cache_btn"):
            load_data.clear()
            load_explanations.clear()
            st.success("Internal cache successfully cleared.")
