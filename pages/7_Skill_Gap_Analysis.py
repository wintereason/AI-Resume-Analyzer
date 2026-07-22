<<<<<<< HEAD
import streamlit as st

from utils.theme import apply_global_styles, page_header, render_empty_state, render_kpi_row, render_skill_chips, section_header
from database import get_connection
from resume_fetch import get_all_resumes
from utils.sidebar import show_sidebar
=======
import html

import streamlit as st

from database import get_connection
from resume_fetch import get_all_resumes
from utils.sidebar import show_sidebar
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)
from utils.skill_gap import get_skill_gap
from auth import require_login

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Skill Gap Analysis | AI Resume Analyzer",
    page_icon="📚",
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
        .gap-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}
        .gap-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.gap-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.gap-hero p{margin:0;max-width:790px;color:rgba(255,255,255,.76);font-size:.8rem}
        .gap-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .overview-card{min-height:112px;padding:16px 17px;border:1px solid var(--line);border-radius:15px;background:#fff;box-shadow:0 7px 20px rgba(35,52,84,.055);position:relative;overflow:hidden}.overview-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--card-accent)}
        .overview-label{color:var(--muted);font-size:.68rem;font-weight:700;text-transform:uppercase}.overview-value{margin-top:10px;color:var(--ink);font-size:1.18rem;font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.overview-note{margin-top:5px;color:#8B96A8;font-size:.66rem}
        .skill-chip{display:inline-block;margin:3px 4px 3px 0;padding:5px 9px;border-radius:999px;color:#215AAA;background:#EDF4FF;border:1px solid #D8E6FB;font-size:.7rem;font-weight:700}
        .empty-state{text-align:center;padding:42px 22px;border:1px dashed #C8D3E3;border-radius:15px;background:#fff}.empty-state .empty-icon{font-size:1.6rem}.empty-state h4{margin:9px 0 3px}.empty-state p{margin:0;font-size:.76rem}
        div[data-testid="stRadio"]{padding:12px 15px;background:#fff;border:1px solid var(--line);border-radius:13px;box-shadow:0 6px 16px rgba(35,52,84,.05)}
        div[data-testid="stSelectbox"]>div>div{background:#fff;border-color:#DDE5F0;border-radius:10px}div[data-testid="stMetric"]{padding:14px;background:#fff;border:1px solid var(--line);border-radius:13px;box-shadow:0 6px 17px rgba(35,52,84,.05)}
        div[data-testid="stMetricValue"]{color:var(--ink);font-weight:800}div[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--blue),var(--cyan))}
        div[data-testid="stAlert"]{border-radius:12px;border-width:1px}div[data-testid="stButton"] button{min-height:43px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}
        div[data-testid="stButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue)}div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;background:var(--blue);color:#fff;border:1px solid var(--blue);font-weight:700}
        hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.gap-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Capability intelligence"):
    st.markdown(
        f'<div class="gap-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></div><div class="gap-icon">{escape(icon or "◎")}</div></div>',
        unsafe_allow_html=True,
    )


def render_skill_chips(skills):
    if not skills:
        st.caption("No skills available.")
        return
    chips = "".join(f'<span class="skill-chip">{escape(skill)}</span>' for skill in skills)
    st.markdown(f'<div style="line-height:2.05">{chips}</div>', unsafe_allow_html=True)


def render_empty_state(title, message, icon="◎"):
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
    title="Skill Gap Analysis",
    description=(
        "Compare a candidate's existing skills with the skills required "
        "for a selected job role."
    ),
    icon="📚",
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


def get_job_roles():
    """
    Fetch available job roles from MySQL.
    """

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                job_role_id,
                job_title
            FROM job_roles
            ORDER BY job_title
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_learning_suggestions(missing_skills):
    """
    Generate simple learning suggestions.
    """

    suggestions = []

    for skill in missing_skills:
        suggestions.append(
            f"Learn the fundamentals of {skill} and complete "
            f"at least one practical project using it."
        )

    return suggestions


def get_match_level(score):
    """
    Return an interpretation of the skill-match score.
    """

    if score >= 80:
        return (
            "Excellent Match",
            "The candidate already has most of the required skills.",
        )

    if score >= 60:
        return (
            "Good Match",
            "The candidate is suitable but should improve a few skills.",
        )

    if score >= 40:
        return (
            "Moderate Match",
            "The candidate needs additional training for this role.",
        )

    return (
        "Low Match",
        "The candidate currently lacks several important job skills.",
    )


# ---------------------------------
# Choose Candidate Source
# ---------------------------------
candidate_source = st.radio(
    "Choose candidate source",
    options=[
        "Currently Uploaded Resume",
        "Saved Candidate",
    ],
    horizontal=True,
)


candidate_name = "Current Candidate"
candidate_email = "Not Available"
resume_skills = []


# ---------------------------------
# Current Uploaded Resume
# ---------------------------------
if candidate_source == "Currently Uploaded Resume":

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

        resume_skills = normalize_skills(current_resume.get("skills"))

    elif "resume_skills" in st.session_state:

        resume_skills = normalize_skills(st.session_state["resume_skills"])

    else:
        st.warning(
            "Please upload and analyse a resume first, or select a saved candidate."
        )
        render_empty_state(
            "No Uploaded Resume",
            "Go to Upload Resume to analyse a candidate first.",
            icon="📤",
        )
        st.stop()


# ---------------------------------
# Saved Candidate
# ---------------------------------
else:

    try:
        saved_candidates = get_all_resumes()

    except Exception as error:
        st.error(f"Unable to load saved candidates: {error}")
        st.stop()

    if not saved_candidates:
        st.info("No candidates are currently saved in the database.")
        st.stop()

    candidate_options = {
        (
            f"{candidate.get('name') or 'Unknown Candidate'} "
            f"— {candidate.get('email') or 'No Email'} "
            f"— ID {candidate.get('id')}"
        ): candidate
        for candidate in saved_candidates
    }

    selected_candidate_label = st.selectbox(
        "Select a saved candidate",
        options=list(candidate_options.keys()),
    )

    selected_candidate = candidate_options[selected_candidate_label]

    candidate_name = selected_candidate.get("name") or "Unknown Candidate"

    candidate_email = selected_candidate.get("email") or "Not Available"

    resume_skills = normalize_skills(selected_candidate.get("skills"))


# ---------------------------------
# Validate Candidate Skills
# ---------------------------------
if not resume_skills:
    st.warning("No skills were found for this candidate.")
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
        "Total Skills",
        len(resume_skills),
    )


with overview_col3:
    st.metric(
        "Email",
        candidate_email,
    )
=======
    overview_card("Candidate", candidate_name, "Selected profile", "#6846C7")


with overview_col2:
    overview_card("Total Skills", len(resume_skills), "Skills currently detected", "#08AFC4")


with overview_col3:
    overview_card("Email", candidate_email, "Candidate contact", "#15B878")
>>>>>>> a1ff58d (Update UI and improve performance)


st.markdown("#### Candidate Skills")
render_skill_chips(resume_skills)


st.divider()


# ---------------------------------
# Load Job Roles
# ---------------------------------
try:
    job_roles = get_job_roles()

except Exception as error:
    st.error(f"Unable to load job roles: {error}")
    st.stop()


if not job_roles:
    st.warning("No job roles are available in the database.")
    st.stop()


job_options = {job["job_title"]: job["job_role_id"] for job in job_roles}


selected_job = st.selectbox(
    "Choose Target Job Role",
    options=list(job_options.keys()),
)


# ---------------------------------
# Analyse Skill Gap
# ---------------------------------
if st.button(
    "🔍 Analyse Skill Gap",
    type="primary",
    width="stretch",
):

    try:
        score, matched, missing = get_skill_gap(
            selected_job,
            resume_skills,
        )

    except Exception as error:
        st.error(f"Unable to analyse the skill gap: {error}")
        st.stop()

    score = float(score or 0)
    score = max(0, min(score, 100))

    matched = normalize_skills(matched)
    missing = normalize_skills(missing)

    total_required_skills = len(matched) + len(missing)

    match_level, match_message = get_match_level(score)

    # Store results for other pages
    st.session_state["skill_gap_result"] = {
        "candidate_name": candidate_name,
        "selected_job": selected_job,
        "score": score,
        "matched": matched,
        "missing": missing,
    }

    st.divider()
    st.subheader("📊 Skill Match Result")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            "Match Score",
            f"{score:.1f}%",
        )

    with metric_col2:
        st.metric(
            "Matched Skills",
            len(matched),
        )

    with metric_col3:
        st.metric(
            "Missing Skills",
            len(missing),
        )

    with metric_col4:
        st.metric(
            "Required Skills",
            total_required_skills,
        )

    st.progress(score / 100)

    if score >= 80:
        st.success(f"✅ {match_level}: {match_message}")

    elif score >= 60:
        st.warning(f"⚠️ {match_level}: {match_message}")

    else:
        st.error(f"❌ {match_level}: {match_message}")

    st.divider()

    # ---------------------------------
    # Matched and Missing Skills
    # ---------------------------------
    matched_column, missing_column = st.columns(2)

    with matched_column:

        st.success("✅ Skills the Candidate Has")

        if matched:
            for skill in matched:
                st.write("✔", skill)

        else:
            st.write("No required skills were matched.")

    with missing_column:

        st.error("❌ Skills the Candidate Needs")

        if missing:
            for skill in missing:
                st.write("✖", skill)

        else:
            st.write("No required skills are missing.")

    st.divider()

    # ---------------------------------
    # Skill Progress
    # ---------------------------------
    st.subheader("📈 Required Skill Progress")

    for skill in matched:
        st.write(f"✅ **{skill}**")
        st.progress(1.0)

    for skill in missing:
        st.write(f"❌ **{skill}**")
        st.progress(0.0)

    st.divider()

    # ---------------------------------
    # Learning Suggestions
    # ---------------------------------
    st.subheader("🎓 Learning Recommendations")

    learning_suggestions = get_learning_suggestions(missing)

    if learning_suggestions:

        for index, suggestion in enumerate(
            learning_suggestions,
            start=1,
        ):
            st.write(f"**{index}.** {suggestion}")

    else:
        st.success("The candidate already has all required skills " "for this role.")

    st.divider()

    # ---------------------------------
    # Suggested Learning Plan
    # ---------------------------------
    st.subheader("🗓 Suggested Learning Plan")

    if missing:

        weeks = min(
            max(len(missing), 2),
            8,
        )

        st.write(
            f"A suggested **{weeks}-week learning plan** "
            f"for the {selected_job} role:"
        )

        for index, skill in enumerate(
            missing,
            start=1,
        ):

            week_number = min(index, weeks)

            st.write(f"**Week {week_number}: {skill}**")

            st.write(f"- Learn the basic concepts of {skill}")

            st.write(f"- Practise with small exercises")

            st.write(f"- Build one mini-project using {skill}")

    else:
        st.success("No additional learning plan is required.")

    st.divider()

    # ---------------------------------
    # Download Skill Gap Report
    # ---------------------------------
    st.subheader("📥 Download Skill Gap Report")

    report_lines = [
        "AI RESUME ANALYZER - SKILL GAP REPORT",
        "",
        f"Candidate: {candidate_name}",
        f"Email: {candidate_email}",
        f"Target Job Role: {selected_job}",
        f"Skill Match Score: {score:.1f}%",
        f"Match Level: {match_level}",
        "",
        "Candidate Skills:",
        ", ".join(resume_skills),
        "",
        "Matched Skills:",
        ", ".join(matched) if matched else "None",
        "",
        "Missing Skills:",
        ", ".join(missing) if missing else "None",
        "",
        "Learning Recommendations:",
    ]

    if learning_suggestions:
        for index, suggestion in enumerate(
            learning_suggestions,
            start=1,
        ):
            report_lines.append(f"{index}. {suggestion}")

    else:
        report_lines.append("No additional skills are currently required.")

    report_text = "\n".join(report_lines)

    safe_candidate_name = candidate_name.replace(" ", "_").replace("/", "_")

    safe_job_name = selected_job.replace(" ", "_").replace("/", "_")

    st.download_button(
        label="⬇️ Download Skill Gap Report",
        data=report_text,
        file_name=(f"{safe_candidate_name}_" f"{safe_job_name}_skill_gap.txt"),
        mime="text/plain",
        width="stretch",
    )


st.caption("AI Resume Analyzer v1.0 | Skill Gap Analysis")
