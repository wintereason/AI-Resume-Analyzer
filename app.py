<<<<<<< HEAD
=======
import html

>>>>>>> a1ff58d (Update UI and improve performance)
import streamlit as st

from dashboard_queries import (
    get_average_ats,
    get_total_job_roles,
    get_total_resumes,
    get_total_skills,
)
from utils.sidebar import show_sidebar
<<<<<<< HEAD
from utils.theme import (
    apply_global_styles,
    page_header,
    render_kpi_row,
    section_header,
)
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

<<<<<<< HEAD
apply_global_styles()
show_sidebar()
=======

def escape(value):
    return html.escape(str(value or ""), quote=True)


def apply_global_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;--blue:#2466D1;--purple:#6846C7}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding:1rem 1.4rem 2.5rem}h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}
        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;border-color:#E4EAF4;transform:translateX(2px)}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}.sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}.sidebar-account .meta{color:#8490A4;font-size:.66rem}.candidate-avatar{display:flex;align-items:center;justify-content:center;flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}.status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}.sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}
        .home-hero{display:flex;justify-content:space-between;align-items:center;gap:25px;padding:30px 30px;margin-bottom:16px;border-radius:20px;color:#fff;background:radial-gradient(circle at 85% 10%,rgba(255,255,255,.16),transparent 32%),linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 14px 32px rgba(37,78,150,.2)}.home-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.home-hero h1{margin:5px 0;color:#fff;font-size:1.8rem;font-weight:800}.home-hero p{margin:0;max-width:830px;color:rgba(255,255,255,.76);font-size:.84rem;line-height:1.6}.home-icon{width:64px;height:64px;display:flex;align-items:center;justify-content:center;flex:0 0 64px;border-radius:18px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.7rem}
        .section-heading{margin:21px 0 10px}.section-heading h3{margin:0;color:var(--ink);font-size:.98rem;font-weight:800}.section-heading p{margin:3px 0 0;color:var(--muted);font-size:.72rem}
        .home-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;box-shadow:0 9px 21px rgba(39,55,93,.12)}.home-metric:after{content:"";position:absolute;width:90px;height:90px;right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}.metric-icon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}.metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;font-size:1.48rem;font-weight:800;line-height:1}.metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}
        div[data-testid="stVerticalBlockBorderWrapper"]{min-height:142px;background:#fff;border-color:var(--line)!important;border-radius:15px!important;box-shadow:0 7px 20px rgba(35,52,84,.055);transition:transform .17s ease,box-shadow .17s ease}div[data-testid="stVerticalBlockBorderWrapper"]:hover{transform:translateY(-2px);box-shadow:0 11px 25px rgba(35,52,84,.09)}
        div[data-testid="stButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}div[data-testid="stButton"] button:hover{color:var(--blue);border-color:#AEC3E5}div[data-testid="stButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue);box-shadow:0 7px 16px rgba(36,102,209,.16)}hr{border-color:#E7EBF2;margin:1.3rem 0}@media(max-width:850px){.home-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title,description="",icon="",eyebrow="Smart recruitment platform"):
    st.markdown(f'<div class="home-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></div><div class="home-icon">{escape(icon or "✦")}</div></div>',unsafe_allow_html=True)


def section_header(title,description="",icon=""):
    prefix=f"{escape(icon)} " if icon else ""
    st.markdown(f'<div class="section-heading"><h3>{prefix}{escape(title)}</h3><p>{escape(description)}</p></div>',unsafe_allow_html=True)


def render_kpi_row(cards):
    colors=[("#5147C6","#6655D5"),("#0879B9","#1598D0"),("#0797AB","#09B8C4"),("#13A875","#1BC58A")]
    columns=st.columns(len(cards))
    for index,(column,card) in enumerate(zip(columns,cards)):
        start,end=colors[index%len(colors)]
        with column:
            st.markdown(f'<div class="home-metric" style="background:linear-gradient(135deg,{start},{end})"><div class="metric-icon">{escape(card.get("icon"))}</div><div class="metric-label">{escape(card.get("label"))}</div><div class="metric-value">{escape(card.get("value"))}</div><div class="metric-note">Live platform data</div></div>',unsafe_allow_html=True)

apply_global_styles()
show_sidebar()
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)

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
