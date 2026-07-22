import streamlit as st

from dashboard_queries import (
    get_average_ats,
    get_total_job_roles,
    get_total_resumes,
    get_total_skills,
)
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    page_header,
    render_kpi_row,
    section_header,
)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
show_sidebar()

# ---------------------------------
# Load Summary Statistics
# ---------------------------------
try:
    total_resumes = get_total_resumes()
    average_ats = float(get_average_ats() or 0)
    total_skills = get_total_skills()
    total_job_roles = get_total_job_roles()

except Exception as error:
    print(f"Home stats error: {error}")
    total_resumes = 0
    average_ats = 0
    total_skills = 0
    total_job_roles = 0

page_header(
    title="AI Resume Analyzer",
    description=(
        "An intelligent recruitment platform for resume screening, ATS scoring, "
        "job matching, skill-gap analysis, candidate ranking, and recruiter decision support."
    ),
    icon="🤖",
)

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("Upload and Analyse Resume", type="primary", width="stretch"):
        st.switch_page("pages/2_Upload_Resume.py")

with action_col2:
    if st.button("Browse Saved Candidates", width="stretch"):
        st.switch_page("pages/3_Saved_Resumes.py")

with action_col3:
    if st.button("Open Recruiter Dashboard", width="stretch"):
        st.switch_page("pages/7_Recruiter_Dashboard.py")

st.divider()

section_header("Platform Overview", "Live recruitment metrics", icon="📊")

render_kpi_row(
    [
        {"label": "Saved Resumes", "value": total_resumes, "icon": "📄"},
        {"label": "Average ATS", "value": f"{average_ats:.1f}%", "icon": "⭐"},
        {"label": "Skills Detected", "value": total_skills, "icon": "💻"},
        {"label": "Available Job Roles", "value": total_job_roles, "icon": "💼"},
    ]
)

st.divider()

section_header("Core Capabilities", icon="✨")

feature_col1, feature_col2, feature_col3 = st.columns(3)

features = [
    (
        "Resume Intelligence",
        "Extract candidate name, email, phone, education, skills, and projects.",
    ),
    (
        "ATS Analysis",
        "Calculate compatibility, identify matched and missing skills, and generate feedback.",
    ),
    (
        "Job Matching",
        "Recommend suitable roles and rank candidates by job requirements.",
    ),
    (
        "Skill Gap Analysis",
        "Compare candidate skills with target-job requirements.",
    ),
    (
        "Recruiter Assistance",
        "Generate summaries, insights, and skill-based interview questions locally.",
    ),
    (
        "Recruitment Analytics",
        "Monitor ATS scores, top skills, candidate status, and hiring performance.",
    ),
]

for index, (title, description) in enumerate(features):
    column = [feature_col1, feature_col2, feature_col3][index % 3]

    with column:
        with st.container(border=True):
            st.markdown(f"#### {title}")
            st.write(description)

st.divider()

section_header("Quick Navigation", icon="⚡")

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.markdown("#### Candidate Operations")

    for label, page in [
        ("Open Main Dashboard", "pages/1_Dashboard.py"),
        ("Upload Resume", "pages/2_Upload_Resume.py"),
        ("Manage Saved Resumes", "pages/3_Saved_Resumes.py"),
        ("Analyse Skill Gap", "pages/7_Skill_Gap_Analysis.py"),
        ("Candidate Profiles", "pages/11_Candidate_Profile.py"),
        ("Interview Scheduler", "pages/12_Interview_Scheduler.py"),
    ]:
        if st.button(label, width="stretch", key=f"nav_candidate_{label}"):
            st.switch_page(page)

with nav_col2:
    st.markdown("#### Recruiter Operations")

    for label, page in [
        ("View Analytics", "pages/4_Analytics.py"),
        ("Job Recommendations", "pages/6_Job_Recommendations.py"),
        ("Recruiter Dashboard", "pages/7_Recruiter_Dashboard.py"),
        ("Job Matching", "pages/8_Job_Matching.py"),
        ("Local Recruiter Assistant", "pages/9_AI_Recruiter_Assistant.py"),
    ]:
        if st.button(label, width="stretch", key=f"nav_recruiter_{label}"):
            st.switch_page(page)

if st.session_state.get("logged_in") and st.session_state.get("user_role") == "Admin":
    st.divider()

    if st.button("User Management", width="stretch"):
        st.switch_page("pages/10_Admin_User_Management.py")

st.caption("AI Resume Analyzer v1.0 | Smart Recruitment Platform")
