import os
from pathlib import Path
from uuid import uuid4

import streamlit as st

from auth import require_role
from ats import calculate_ats_score
from extractor import (
    extract_education,
    extract_email,
    extract_name,
    extract_phone,
    extract_projects,
    extract_skills,
)
from resume_database import save_resume
from resume_parser import extract_text_from_pdf
from utils.ai_feedback import generate_feedback
from utils.pdf_report import generate_pdf
from utils.recommendation import recommend_jobs
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    page_header,
    render_kpi_row,
    render_progress_steps,
    render_skill_chips,
    render_status_badge,
    section_header,
)

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Upload Resume | AI Resume Analyzer",
    page_icon="📤",
    layout="wide",
)


# ---------------------------------
# Authentication and Styling
# ---------------------------------
apply_global_styles()
require_role(["Admin", "Recruiter"])
show_sidebar()


# ---------------------------------
# Helper Functions
# ---------------------------------
def normalize_list(value):
    """
    Convert extracted values into a clean list.
    """

    if value is None:
        return []

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]

    return [str(value).strip()]


def display_value(value, default="Not Found"):
    """
    Return a safe value for displaying extracted information.
    """

    if value is None:
        return default

    cleaned_value = str(value).strip()

    return cleaned_value if cleaned_value else default


def determine_status(score):
    """
    Assign an initial recruitment status using ATS score.
    """

    if score >= 80:
        return "Shortlisted"

    if score >= 60:
        return "Under Review"

    return "Review Required"


def get_primary_recommendation(recommendations):
    """
    Safely retrieve the first recommended job role.
    """

    if not recommendations:
        return "Not Assigned"

    if isinstance(recommendations, str):
        return recommendations.strip() or "Not Assigned"

    if isinstance(recommendations, (list, tuple)):
        first_recommendation = recommendations[0]

        if isinstance(first_recommendation, dict):
            return (
                first_recommendation.get("job")
                or first_recommendation.get("role")
                or first_recommendation.get("job_role")
                or first_recommendation.get("title")
                or "Not Assigned"
            )

        return str(first_recommendation).strip() or "Not Assigned"

    return str(recommendations).strip() or "Not Assigned"


def create_unique_pdf_path(uploaded_file):
    """
    Create a unique and safe destination path for an uploaded PDF.
    """

    upload_directory = Path("Upload")
    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    original_stem = Path(uploaded_file.name).stem

    safe_stem = "".join(
        character
        for character in original_stem
        if character.isalnum() or character in (" ", "-", "_")
    ).strip()

    safe_stem = safe_stem.replace(" ", "_") or "resume"

    unique_filename = f"{safe_stem}_{uuid4().hex[:8]}.pdf"

    return upload_directory / unique_filename


def format_recommendation_role(recommendation):
    """
    Return a readable job title from a recommendation.
    """

    if isinstance(recommendation, dict):
        return (
            recommendation.get("job")
            or recommendation.get("role")
            or recommendation.get("job_role")
            or recommendation.get("title")
            or "Recommended Role"
        )

    return str(recommendation)


def get_recommendation_score(recommendation):
    """
    Return a job recommendation score safely.
    """

    if not isinstance(recommendation, dict):
        return None

    score = recommendation.get("score") or recommendation.get("match_score")

    try:
        return float(score)

    except (TypeError, ValueError):
        return None


def run_resume_analysis(file_path):
    """Run full resume extraction, ATS scoring, and recommendations."""
    with st.spinner("Reading and analysing the resume..."):
        text = extract_text_from_pdf(str(file_path))

    if not text or not text.strip():
        raise ValueError(
            "No readable text was found in this PDF. "
            "The file may contain scanned images instead of selectable text."
        )

    resume_data = {
        "name": display_value(extract_name(text)),
        "email": display_value(extract_email(text)),
        "phone": display_value(extract_phone(text)),
        "skills": normalize_list(extract_skills(text)),
        "education": normalize_list(extract_education(text)),
        "projects": normalize_list(extract_projects(text)),
        "resume_file": str(file_path),
    }

    required_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "Power BI",
        "Git",
        "Communication",
    ]

    score, matched, missing = calculate_ats_score(
        resume_data["skills"],
        required_skills,
    )

    score = max(0, min(float(score or 0), 100))
    matched = normalize_list(matched)
    missing = normalize_list(missing)
    resume_data["ats_score"] = score

    try:
        feedback = generate_feedback(resume_data)
    except Exception as error:
        print(f"Feedback generation error: {error}")
        feedback = {
            "rating": round(score / 10, 1),
            "strengths": [],
            "suggestions": [],
        }

    try:
        recommendations = recommend_jobs(resume_data["skills"])
    except Exception as error:
        print(f"Recommendation error: {error}")
        recommendations = []

    recommended_role = get_primary_recommendation(recommendations)
    candidate_status = determine_status(score)

    resume_data["recommended_role"] = recommended_role
    resume_data["status"] = candidate_status
    resume_data["performed_by"] = st.session_state.get("user_id")

    return {
        "resume_data": resume_data,
        "score": score,
        "matched": matched,
        "missing": missing,
        "feedback": feedback,
        "recommendations": recommendations,
        "recommended_role": recommended_role,
        "candidate_status": candidate_status,
    }


# ---------------------------------
# Page Header
# ---------------------------------
page_header(
    title="Upload Resume",
    description=(
        "Guide each resume through a polished intake workflow that extracts profile data, calculates ATS fit, and prepares recruiter-ready insights."
    ),
    icon="📤",
    eyebrow="Resume Intake",
)


# ---------------------------------
# Resume Upload
# ---------------------------------
render_progress_steps(["Upload", "Parse", "ATS", "Recommend", "Save"], 0)

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a Resume",
    type=["pdf"],
    help="Only PDF resume files are currently supported.",
)


if uploaded_file is None:
    st.info("Upload a PDF resume to begin the analysis.")
    st.stop()


# ---------------------------------
# Save Uploaded PDF
# ---------------------------------
# Create a new path only when the uploaded file changes.
uploaded_file_key = (
    uploaded_file.name,
    uploaded_file.size,
)


if st.session_state.get("uploaded_file_key") != uploaded_file_key:
    file_path = create_unique_pdf_path(uploaded_file)

    try:
        file_path.write_bytes(uploaded_file.getbuffer())

    except OSError as error:
        st.error(f"Unable to save the uploaded resume: {error}")
        st.stop()

    st.session_state["uploaded_file_key"] = uploaded_file_key
    st.session_state["uploaded_resume_path"] = str(file_path)
    st.session_state["current_resume_saved"] = False
    st.session_state.pop("saved_resume_id", None)
    st.session_state.pop("upload_analysis_cache", None)


file_path = Path(st.session_state["uploaded_resume_path"])


if not file_path.exists():
    st.error("The uploaded PDF could not be found. Please upload the file again.")
    st.stop()


with st.container(border=True):
    st.success(f"Resume uploaded: {uploaded_file.name}")
    st.caption(f"Stored as: {file_path.name}")
    st.caption("The file is now ready for parsing, ATS scoring, and recruiter review.")


# ---------------------------------
# Run or reuse cached analysis
# ---------------------------------
cache_key = st.session_state.get("uploaded_file_key")

if st.session_state.get("upload_analysis_key") != cache_key:
    try:
        analysis = run_resume_analysis(file_path)
        st.session_state["upload_analysis_key"] = cache_key
        st.session_state["upload_analysis_cache"] = analysis
    except ValueError as error:
        st.error(str(error))
        st.stop()
    except Exception as error:
        st.error("Unable to analyse the resume. Please try another PDF.")
        print(f"Resume analysis error: {error}")
        st.stop()

analysis = st.session_state["upload_analysis_cache"]
resume_data = analysis["resume_data"]
score = analysis["score"]
matched = analysis["matched"]
missing = analysis["missing"]
feedback = analysis["feedback"]
recommendations = analysis["recommendations"]
recommended_role = analysis["recommended_role"]
candidate_status = analysis["candidate_status"]

st.session_state["resume_skills"] = resume_data["skills"]
st.session_state["current_resume"] = resume_data.copy()


# ---------------------------------
# Analysis status
# ---------------------------------
render_progress_steps(["Upload", "Parse", "ATS", "Recommend", "Save"], 3)

section_header(
    "Analysis Status",
    "Resume parsing, ATS scoring, and recommendations are complete.",
    icon="✅",
)


render_kpi_row(
    [
        {"label": "ATS Score", "value": f"{score:.1f}%", "icon": "⭐"},
        {"label": "Recommended Role", "value": recommended_role, "icon": "💼"},
        {"label": "Status", "value": candidate_status, "icon": "📌"},
    ]
)


# ---------------------------------
# Candidate details
# ---------------------------------
st.divider()
section_header(
    "Candidate Details",
    "Information extracted from the uploaded resume",
    icon="📄",
)

left_column, right_column = st.columns(2)


with left_column:
    with st.container(border=True):
        st.markdown("#### 👤 Candidate Information")

        st.write("**Name**")
        st.success(resume_data["name"])

        st.write("**Email**")
        st.info(resume_data["email"])

        st.write("**Phone**")
        st.info(resume_data["phone"])

        st.markdown("#### 🎓 Education")

        if resume_data["education"]:
            for education_item in resume_data["education"]:
                st.write("•", education_item)

        else:
            st.write("No education information found.")


with right_column:
    with st.container(border=True):
        st.markdown("#### Skills")
        render_skill_chips(resume_data["skills"])

        st.markdown("#### Projects")

        if resume_data["projects"]:
            for project in resume_data["projects"]:
                st.write("•", project)
        else:
            st.write("No projects found.")

        st.markdown("#### Recommended Role")
        st.caption(recommended_role)


# ---------------------------------
# ATS overview
# ---------------------------------
st.divider()
section_header("ATS Overview", "Compatibility score and skill alignment", icon="⭐")

metric_column1, metric_column2, metric_column3 = st.columns(3)


with metric_column1:
    st.metric(
        label="ATS Score",
        value=f"{score:.1f}%",
    )


with metric_column2:
    st.metric(
        label="Recommended Role",
        value=recommended_role,
    )


with metric_column3:
    st.metric(label="Candidate Status", value=candidate_status)
    render_status_badge(candidate_status)


st.progress(score / 100)


if score >= 80:
    st.success("Excellent resume. The candidate is " "highly ATS compatible.")

elif score >= 60:
    st.warning("Good resume. Adding more relevant skills " "may improve the ATS score.")

else:
    st.error(
        "The ATS score is low. The resume needs "
        "stronger relevant skills and better "
        "job-specific content."
    )


matched_column, missing_column = st.columns(2)


with matched_column:
    with st.container(border=True):
        st.success("✅ Matched Skills")

        if matched:
            for skill in matched:
                st.write("✔", skill)

        else:
            st.write("No matching skills found.")


with missing_column:
    with st.container(border=True):
        st.error("❌ Missing Skills")

        if missing:
            for skill in missing:
                st.write("✖", skill)

        else:
            st.write("No required skills are missing.")


# ---------------------------------
# Job Recommendations
# ---------------------------------
st.divider()
section_header(
    "Job Recommendations",
    "Roles matched to extracted skills",
    icon="💼",
)


if recommendations:
    recommendation_items = (
        [recommendations] if isinstance(recommendations, str) else recommendations
    )

    for index, recommendation in enumerate(
        recommendation_items,
        start=1,
    ):
        role = format_recommendation_role(recommendation)

        match_score = get_recommendation_score(recommendation)

        with st.container(border=True):
            role_column, score_column = st.columns([3, 1])

            with role_column:
                st.markdown(f"#### {index}. {role}")

                if isinstance(
                    recommendation,
                    dict,
                ):
                    demand = recommendation.get("demand")

                    if demand:
                        st.write(f"**Demand:** {demand}")

            with score_column:
                if match_score is not None:
                    st.metric(
                        "Match",
                        f"{match_score:.1f}%",
                    )

else:
    st.info("No suitable job recommendation was found " "for the extracted skills.")


# ---------------------------------
# Resume Feedback
# ---------------------------------
st.divider()
section_header(
    "Resume Feedback",
    "Rule-based strengths and improvement suggestions",
    icon="🤖",
)


rating = feedback.get(
    "rating",
    round(score / 10, 1),
)

strengths = normalize_list(feedback.get("strengths"))

suggestions = normalize_list(feedback.get("suggestions"))


st.metric(
    label="Resume Rating",
    value=f"{rating}/10",
)


feedback_column1, feedback_column2 = st.columns(2)


with feedback_column1:
    with st.container(border=True):
        st.success("✅ Resume Strengths")

        if strengths:
            for item in strengths:
                st.write("✔", item)

        else:
            st.write("No specific strengths were generated.")


with feedback_column2:
    with st.container(border=True):
        st.warning("⚠️ Improvement Suggestions")

        if suggestions:
            for item in suggestions:
                st.write("➤", item)

        else:
            st.write("No improvement suggestions " "were generated.")


# ---------------------------------
# Actions
# ---------------------------------
st.divider()
section_header("Actions", "Save candidate or generate a PDF report", icon="⚡")

save_column, report_column = st.columns(2)


with save_column:
    already_saved = st.session_state.get(
        "current_resume_saved",
        False,
    )

    if already_saved:
        saved_resume_id = st.session_state.get("saved_resume_id")

        st.success(
            "✅ This resume is already saved"
            + (f" as Candidate ID {saved_resume_id}." if saved_resume_id else ".")
        )

    if st.button(
        "💾 Save Resume",
        width="stretch",
        type="primary",
        disabled=already_saved,
    ):
        try:
            resume_id = save_resume(resume_data)

            st.session_state["current_resume_saved"] = True

            st.session_state["saved_resume_id"] = resume_id

            st.success("✅ Resume saved successfully. " f"Candidate ID: {resume_id}")

            st.rerun()

        except Exception as error:
            st.error(f"Database error: {error}")


with report_column:
    if st.button(
        "📄 Generate PDF Report",
        width="stretch",
    ):
        try:
            pdf_path = generate_pdf(
                resume_data,
                recommendations,
                feedback,
                matched,
                missing,
            )

            if not os.path.exists(pdf_path):
                st.error("The PDF report file was not created.")

            else:
                pdf_file_path = Path(pdf_path)

                with open(
                    pdf_file_path,
                    "rb",
                ) as file:
                    st.download_button(
                        label="⬇️ Download ATS Report",
                        data=file.read(),
                        file_name=pdf_file_path.name,
                        mime="application/pdf",
                        width="stretch",
                    )

        except Exception as error:
            st.error("Unable to generate the PDF report: " f"{error}")


st.caption("AI Resume Analyzer v1.0 | " "Resume Upload and Analysis")
