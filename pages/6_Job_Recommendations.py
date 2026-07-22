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
from resume_fetch import get_all_resumes
from utils.recommendation import recommend_jobs
from utils.recruiter_matching import (
    generate_interview_questions,
    generate_recruiter_summary,
)
from utils.sidebar import show_sidebar
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


# ---------------------------------
# Sidebar
# ---------------------------------
show_sidebar()
apply_global_styles()
require_login()

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
