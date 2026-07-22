import streamlit as st

from utils.theme import apply_global_styles, page_header, render_empty_state, render_kpi_row, render_skill_chips, section_header
from database import get_connection
from resume_fetch import get_all_resumes
from utils.sidebar import show_sidebar
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


# ---------------------------------
# Sidebar
# ---------------------------------
show_sidebar()
apply_global_styles()
require_login()

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
