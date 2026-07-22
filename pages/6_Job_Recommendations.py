<<<<<<< HEAD
import pandas as pd
import streamlit as st

from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    render_kpi_row,
    render_skill_chips,
    section_header,
)
=======
import html

import pandas as pd
import streamlit as st

>>>>>>> a1ff58d (Update UI and improve performance)
from resume_fetch import get_all_resumes
from utils.recommendation import recommend_jobs
from utils.recruiter_matching import (
    generate_interview_questions,
    generate_recruiter_summary,
)
from utils.sidebar import show_sidebar
<<<<<<< HEAD
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)
from auth import require_login

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Job Recommendations | AI Resume Analyzer",
    page_icon="💼",
    layout="wide",
)


<<<<<<< HEAD
=======
def escape(value):
    return html.escape(str(value or ""), quote=True)


def apply_global_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;--blue:#2466D1;
        --cyan:#08AFC4;--green:#15B878;--amber:#F3A536;--purple:#6846C7;--red:#E6556D}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}
        header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1460px;padding:1rem 1.4rem 2.5rem}
        h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}
        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;border-color:#E4EAF4;transform:translateX(2px)}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
        .sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}.sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}.sidebar-account .meta{color:#8490A4;font-size:.66rem}
        .candidate-avatar{display:flex;align-items:center;justify-content:center;flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}.status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}
        .sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}
        .jobs-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}
        .jobs-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.jobs-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.jobs-hero p{margin:0;max-width:790px;color:rgba(255,255,255,.76);font-size:.8rem}
        .jobs-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .overview-card{min-height:112px;padding:16px 17px;border:1px solid var(--line);border-radius:15px;background:#fff;box-shadow:0 7px 20px rgba(35,52,84,.055);position:relative;overflow:hidden}.overview-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--card-accent)}
        .overview-label{color:var(--muted);font-size:.68rem;font-weight:700;text-transform:uppercase}.overview-value{margin-top:10px;color:var(--ink);font-size:1.2rem;font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.overview-note{margin-top:5px;color:#8B96A8;font-size:.66rem}
        .skill-chip{display:inline-block;margin:3px 4px 3px 0;padding:5px 9px;border-radius:999px;color:#215AAA;background:#EDF4FF;border:1px solid #D8E6FB;font-size:.7rem;font-weight:700}
        .empty-state{text-align:center;padding:42px 22px;border:1px dashed #C8D3E3;border-radius:15px;background:#fff}.empty-state .empty-icon{font-size:1.6rem}.empty-state h4{margin:9px 0 3px}.empty-state p{margin:0;font-size:.76rem}
        div[data-testid="stRadio"]{padding:12px 15px;background:#fff;border:1px solid var(--line);border-radius:13px;box-shadow:0 6px 16px rgba(35,52,84,.05)}
        div[data-testid="stSelectbox"]>div>div{background:#fff;border-color:#DDE5F0;border-radius:10px}div[data-testid="stExpander"]{margin-bottom:9px;background:#fff;border:1px solid var(--line);border-radius:13px!important;box-shadow:0 6px 17px rgba(35,52,84,.05);overflow:hidden}
        div[data-testid="stMetric"]{padding:14px;background:#F8FAFD;border:1px solid var(--line);border-radius:12px}div[data-testid="stMetricValue"]{color:var(--ink);font-weight:800}
        div[data-testid="stAlert"]{border-radius:12px;border-width:1px}div[data-testid="stSlider"]{padding:4px 2px}.stSlider [data-baseweb="slider"] div[role="slider"]{background:var(--blue)}
        div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700;background:var(--blue);color:#fff;width:100%}
        hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.jobs-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Role intelligence"):
    st.markdown(
        f'<div class="jobs-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></div><div class="jobs-icon">{escape(icon or "◇")}</div></div>',
        unsafe_allow_html=True,
    )


def render_skill_chips(skills):
    if not skills:
        st.caption("No skills available.")
        return
    chips = "".join(f'<span class="skill-chip">{escape(skill)}</span>' for skill in skills)
    st.markdown(f'<div style="line-height:2.05">{chips}</div>', unsafe_allow_html=True)


def render_empty_state(title, message, icon="◇"):
    st.markdown(
        f'<div class="empty-state"><div class="empty-icon">{escape(icon)}</div><h4>{escape(title)}</h4><p>{escape(message)}</p></div>',
        unsafe_allow_html=True,
    )


def overview_card(label, value, note, accent):
    st.markdown(
        f'<div class="overview-card" style="--card-accent:{accent}"><div class="overview-label">{escape(label)}</div>'
        f'<div class="overview-value" title="{escape(value)}">{escape(value)}</div><div class="overview-note">{escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


>>>>>>> a1ff58d (Update UI and improve performance)
# ---------------------------------
# Sidebar
# ---------------------------------
show_sidebar()
apply_global_styles()
require_login()
<<<<<<< HEAD
=======
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)

page_header(
    title="Job Recommendations",
    description=(
        "Analyse candidate skills, identify suitable job roles, "
        "generate recruiter summaries, and prepare interview questions."
    ),
    icon="💼",
)
# ---------------------------------
def normalize_skills(value):
    """
    Convert skills into a clean list.
    """

    if value is None:
        return []

    if isinstance(value, str):
        return [skill.strip() for skill in value.split(",") if skill.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(skill).strip() for skill in value if str(skill).strip()]

    return [str(value).strip()]


def get_job_name(job):
    """
    Safely retrieve a job title from a recommendation.
    """

    if not isinstance(job, dict):
        return str(job)

    return (
        job.get("job")
        or job.get("role")
        or job.get("job_role")
        or job.get("title")
        or "Recommended Role"
    )


def get_job_score(job):
    """
    Safely retrieve the job-match score.
    """

    if not isinstance(job, dict):
        return 0

    score = job.get("score") or job.get("match_score") or 0

    try:
        return float(score)

    except (TypeError, ValueError):
        return 0


# ---------------------------------
# Select Candidate Source
# ---------------------------------
source = st.radio(
    "Choose candidate source",
    options=[
        "Currently Uploaded Resume",
        "Saved Candidate",
    ],
    horizontal=True,
)


candidate_name = "Current Candidate"
candidate_email = "Not Available"
candidate_ats = 0
candidate_status = "Under Review"
candidate_education = ""
candidate_projects = ""
resume_skills = []


# ---------------------------------
# Current Uploaded Resume
# ---------------------------------
if source == "Currently Uploaded Resume":

    if "current_resume" in st.session_state:

        current_resume = st.session_state["current_resume"]

        candidate_name = current_resume.get(
            "name",
            "Current Candidate",
        )

        candidate_email = current_resume.get(
            "email",
            "Not Available",
        )

        candidate_ats = current_resume.get(
            "ats_score",
            0,
        )

        candidate_status = current_resume.get(
            "status",
            "Under Review",
        )

        candidate_education = current_resume.get(
            "education",
            "",
        )

        candidate_projects = current_resume.get(
            "projects",
            "",
        )

        resume_skills = normalize_skills(current_resume.get("skills"))

    elif "resume_skills" in st.session_state:

        resume_skills = normalize_skills(st.session_state["resume_skills"])

    else:
        st.warning(
            "Please upload and analyse a resume first, or select a saved candidate."
        )
        render_empty_state(
            "No Candidate Selected",
            "Upload a resume or choose a saved candidate to continue.",
            icon="💼",
        )
        st.stop()


# ---------------------------------
# Saved Candidate
# ---------------------------------
else:

    try:
        saved_resumes = get_all_resumes()

    except Exception as error:
        st.error(f"Unable to load saved candidates: {error}")
        st.stop()

    if not saved_resumes:
        st.info("No candidates are saved in the database.")
        st.stop()

    candidate_options = {
        (
            f"{candidate.get('name') or 'Unknown Candidate'} "
            f"— {candidate.get('email') or 'No Email'} "
            f"— ID {candidate.get('id')}"
        ): candidate
        for candidate in saved_resumes
    }

    selected_candidate_label = st.selectbox(
        "Select a saved candidate",
        options=list(candidate_options.keys()),
    )

    selected_candidate = candidate_options[selected_candidate_label]

    candidate_name = selected_candidate.get("name") or "Unknown Candidate"

    candidate_email = selected_candidate.get("email") or "Not Available"

    candidate_ats = selected_candidate.get("ats_score") or 0

    candidate_status = selected_candidate.get("status") or "Under Review"

    candidate_education = selected_candidate.get("education") or ""

    candidate_projects = selected_candidate.get("projects") or ""

    resume_skills = normalize_skills(selected_candidate.get("skills"))


# ---------------------------------
# Validate Candidate Skills
# ---------------------------------
if not resume_skills:
    st.warning(
        "No skills were found for this candidate. "
        "Job recommendations cannot be generated."
    )
    st.stop()


# ---------------------------------
# Candidate Overview
# ---------------------------------
st.subheader("👤 Candidate Overview")


overview_col1, overview_col2, overview_col3 = st.columns(3)


with overview_col1:
<<<<<<< HEAD
    st.metric(
        "Candidate",
        candidate_name,
    )


with overview_col2:
    st.metric(
        "ATS Score",
        f"{float(candidate_ats or 0):.1f}%",
    )


with overview_col3:
    st.metric(
        "Status",
        candidate_status,
    )
=======
    overview_card("Candidate", candidate_name, candidate_email, "#6846C7")


with overview_col2:
    overview_card("ATS Score", f"{float(candidate_ats or 0):.1f}%", "Resume compatibility", "#08AFC4")


with overview_col3:
    overview_card("Status", candidate_status, "Recruitment pipeline", "#15B878")
>>>>>>> a1ff58d (Update UI and improve performance)


st.write(f"**Email:** {candidate_email}")

st.markdown("#### Extracted Skills")
render_skill_chips(resume_skills)


st.divider()


# ---------------------------------
# Generate Job Recommendations
# ---------------------------------
try:
    recommendations = recommend_jobs(resume_skills)

except Exception as error:
    st.error(f"Unable to generate job recommendations: {error}")
    st.stop()


if recommendations is None:
    recommendations = []


# Sort recommendations by score
if isinstance(recommendations, list):

    recommendations = sorted(
        recommendations,
        key=get_job_score,
        reverse=True,
    )


# ---------------------------------
# Recruiter Summary
# ---------------------------------
st.subheader("🤖 Recruiter Summary")


top_role = "Not Assigned"
top_score = 0


if recommendations:

    top_role = get_job_name(recommendations[0])

    top_score = get_job_score(recommendations[0])


summary = generate_recruiter_summary(
    candidate_name=candidate_name,
    skills=resume_skills,
    ats_score=candidate_ats,
    recommended_role=top_role,
    match_score=top_score,
    education=candidate_education,
    projects=candidate_projects,
)


st.info(summary)


st.divider()


# ---------------------------------
# Job Recommendations
# ---------------------------------
st.subheader("🎯 Recommended Job Roles")


if not recommendations:
    render_empty_state(
        "No Recommendations",
        "No suitable job recommendations were found for this candidate.",
        icon="🎯",
    )

else:

    for index, job in enumerate(
        recommendations,
        start=1,
    ):

        job_name = get_job_name(job)
        score = get_job_score(job)

        matched_skills = normalize_skills(
            job.get("matched") if isinstance(job, dict) else []
        )

        missing_skills = normalize_skills(
            job.get("missing") if isinstance(job, dict) else []
        )

        demand = (
            job.get("demand", "Not Available")
            if isinstance(job, dict)
            else "Not Available"
        )

        salary_india = job.get("salary_india") if isinstance(job, dict) else None

        salary_us = job.get("salary_us") if isinstance(job, dict) else None

        with st.expander(
            f"{index}. {job_name} — {score:.1f}% match",
            expanded=index == 1,
        ):

            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric(
                    "Match Score",
                    f"{score:.1f}%",
                )

            with metric_col2:
                st.metric(
                    "Demand",
                    demand,
                )

            with metric_col3:
                st.metric(
                    "Missing Skills",
                    len(missing_skills),
                )

            salary_col1, salary_col2 = st.columns(2)

            with salary_col1:

                if salary_india is not None:

                    try:
                        st.write(f"**India Salary:** " f"₹{int(salary_india):,}")

                    except (TypeError, ValueError):
                        st.write(f"**India Salary:** " f"{salary_india}")

                else:
                    st.write("**India Salary:** Not Available")

            with salary_col2:

                if salary_us is not None:

                    try:
                        st.write(f"**US Salary:** " f"${int(salary_us):,}")

                    except (TypeError, ValueError):
                        st.write(f"**US Salary:** " f"{salary_us}")

                else:
                    st.write("**US Salary:** Not Available")

            skill_col1, skill_col2 = st.columns(2)

            with skill_col1:

                st.success("✅ Matched Skills")

                if matched_skills:
                    for skill in matched_skills:
                        st.write("✔", skill)

                else:
                    st.write("No matched skills found.")

            with skill_col2:

                st.warning("⚠️ Missing Skills")

                if missing_skills:
                    for skill in missing_skills:
                        st.write("➤", skill)

                else:
                    st.write("No missing skills.")


st.divider()


# ---------------------------------
# Interview Questions
# ---------------------------------
st.subheader("🎤 Interview Question Generator")


question_count = st.slider(
    "Number of interview questions",
    min_value=5,
    max_value=15,
    value=8,
    step=1,
)


questions = generate_interview_questions(
    skills=resume_skills,
    job_role=top_role,
    number_of_questions=question_count,
)


if questions:

    for index, question in enumerate(
        questions,
        start=1,
    ):
        st.write(f"**{index}. {question}**")

else:
    st.info("No interview questions could be generated.")


st.divider()


# ---------------------------------
# Download Recruiter Report
# ---------------------------------
st.subheader("📥 Export Recruiter Report")


report_lines = [
    "AI RESUME ANALYZER - RECRUITER REPORT",
    "",
    f"Candidate: {candidate_name}",
    f"Email: {candidate_email}",
    f"ATS Score: {float(candidate_ats or 0):.1f}%",
    f"Candidate Status: {candidate_status}",
    f"Top Recommended Role: {top_role}",
    f"Top Match Score: {top_score:.1f}%",
    "",
    "Skills:",
    ", ".join(resume_skills),
    "",
    "Recruiter Summary:",
    summary,
    "",
    "Interview Questions:",
]


for index, question in enumerate(
    questions,
    start=1,
):
    report_lines.append(f"{index}. {question}")


report_text = "\n".join(report_lines)


st.download_button(
    label="⬇️ Download Recruiter Report",
    data=report_text,
    file_name=(f"{candidate_name.replace(' ', '_')}" "_recruiter_report.txt"),
    mime="text/plain",
    width="stretch",
)


st.caption("AI Resume Analyzer v1.0 | " "Job Recommendation and Interview Support")
