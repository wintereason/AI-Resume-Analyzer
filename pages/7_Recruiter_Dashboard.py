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
from database import get_connection
from utils.recruiter_matching import (
    get_job_skills,
    match_candidates,
)
from utils.sidebar import show_sidebar
from auth import require_login

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Recruiter Dashboard | AI Resume Analyzer",
    page_icon="👨‍💼",
    layout="wide",
)


# ---------------------------------
# Sidebar
# ---------------------------------
show_sidebar()
apply_global_styles()
require_login()

page_header(
    title="Recruiter Dashboard",
    description=(
        "Rank candidates by job requirements, ATS score, matched skills, "
        "and recruitment status."
    ),
    icon="👨‍💼",
)
# ---------------------------------
def get_job_roles():
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


def update_candidate_status(candidate_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE resumes
            SET status = %s
            WHERE id = %s
            """,
            (status, candidate_id),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def normalize_skills(value):
    if value is None:
        return []

    if isinstance(value, str):
        return [skill.strip() for skill in value.split(",") if skill.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(skill).strip() for skill in value if str(skill).strip()]

    return [str(value).strip()]


def calculate_combined_score(match_score, ats_score):
    """
    Final recruiter score:
    70% job-skill match + 30% ATS score
    """

    try:
        match_score = float(match_score or 0)
    except (TypeError, ValueError):
        match_score = 0

    try:
        ats_score = float(ats_score or 0)
    except (TypeError, ValueError):
        ats_score = 0

    return round(
        (match_score * 0.70) + (ats_score * 0.30),
        2,
    )


def get_rank_label(rank):
    if rank == 1:
        return "🥇 1"

    if rank == 2:
        return "🥈 2"

    if rank == 3:
        return "🥉 3"

    return str(rank)


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
    "🎯 Select Target Job Role",
    options=list(job_options.keys()),
)


selected_job_id = job_options[selected_job]


# ---------------------------------
# Load Required Skills
# ---------------------------------
try:
    required_skills = get_job_skills(selected_job_id)

except Exception as error:
    st.error(f"Unable to load required job skills: {error}")
    st.stop()


if not required_skills:
    st.warning(f"No required skills are assigned to {selected_job}.")
    st.stop()


st.markdown("#### Required Skills")

st.write(" • ".join(required_skills))

st.divider()


# ---------------------------------
# Match and Rank Candidates
# ---------------------------------
try:
    candidates = match_candidates(required_skills)

except Exception as error:
    st.error(f"Unable to rank candidates: {error}")
    st.stop()


if not candidates:
    st.info("No saved candidates are available for ranking.")
    st.stop()


for candidate in candidates:
    candidate["combined_score"] = calculate_combined_score(
        candidate.get("match_score"),
        candidate.get("ats_score"),
    )


candidates.sort(
    key=lambda item: item["combined_score"],
    reverse=True,
)


for rank, candidate in enumerate(
    candidates,
    start=1,
):
    candidate["rank"] = rank


df = pd.DataFrame(candidates)


# ---------------------------------
# Dashboard Statistics
# ---------------------------------
total_candidates = len(df)

average_ats = (
    pd.to_numeric(
        df["ats_score"],
        errors="coerce",
    )
    .fillna(0)
    .mean()
)

average_match = (
    pd.to_numeric(
        df["match_score"],
        errors="coerce",
    )
    .fillna(0)
    .mean()
)

high_match_candidates = len(df[df["combined_score"] >= 75])


highest_ats = (
    pd.to_numeric(df["ats_score"], errors="coerce").fillna(0).max()
)


render_kpi_row(
    [
        {"label": "Total Candidates", "value": total_candidates, "icon": "👥"},
        {"label": "Highest ATS", "value": f"{highest_ats:.1f}%", "icon": "🏆"},
        {"label": "Average ATS", "value": f"{average_ats:.1f}%", "icon": "⭐"},
        {"label": "Strong Candidates", "value": high_match_candidates, "icon": "✅"},
    ]
)


st.divider()


# ---------------------------------
# Search and Filters
# ---------------------------------
st.subheader("🔍 Search and Filter")


filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])


with filter_col1:
    search_text = st.text_input(
        "Search candidate",
        placeholder="Search by name, email, or skill",
    )


with filter_col2:
    minimum_match = st.slider(
        "Minimum Job Match",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )


with filter_col3:
    minimum_ats = st.slider(
        "Minimum ATS Score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )


status_options = sorted(
    [str(status) for status in df["status"].dropna().unique() if str(status).strip()]
)


selected_status = st.selectbox(
    "Candidate Status",
    options=["All"] + status_options,
)


filtered_df = df.copy()


if search_text:
    search_value = search_text.strip()

    filtered_df = filtered_df[
        filtered_df["name"].str.contains(
            search_value,
            case=False,
            na=False,
        )
        | filtered_df["email"].str.contains(
            search_value,
            case=False,
            na=False,
        )
        | filtered_df["skills"].apply(
            lambda value: search_value.lower()
            in ", ".join(normalize_skills(value)).lower()
        )
    ]


filtered_df = filtered_df[
    pd.to_numeric(
        filtered_df["match_score"],
        errors="coerce",
    ).fillna(0)
    >= minimum_match
]


filtered_df = filtered_df[
    pd.to_numeric(
        filtered_df["ats_score"],
        errors="coerce",
    ).fillna(0)
    >= minimum_ats
]


if selected_status != "All":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]


st.caption(f"Showing {len(filtered_df)} of " f"{len(df)} ranked candidates")


st.divider()


# ---------------------------------
# Candidate Ranking Table
# ---------------------------------
st.subheader("🏆 Candidate Ranking")


if filtered_df.empty:
    render_empty_state(
        "No Matching Candidates",
        "Adjust your search or filter criteria to see results.",
        icon="🔍",
    )

else:
    ranking_df = filtered_df.copy()

    ranking_df["Rank"] = ranking_df["rank"].apply(get_rank_label)

    ranking_df["Skills"] = ranking_df["skills"].apply(
        lambda value: ", ".join(normalize_skills(value))
    )

    ranking_df["Matched Skills"] = ranking_df["matched_skills"].apply(
        lambda value: ", ".join(normalize_skills(value))
    )

    ranking_df["Missing Skills"] = ranking_df["missing_skills"].apply(
        lambda value: ", ".join(normalize_skills(value))
    )

    ranking_df["ATS Score"] = (
        pd.to_numeric(
            ranking_df["ats_score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
    )

    ranking_df["Job Match"] = (
        pd.to_numeric(
            ranking_df["match_score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
    )

    ranking_df["Final Score"] = (
        pd.to_numeric(
            ranking_df["combined_score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
    )

    ranking_df = ranking_df[
        [
            "Rank",
            "name",
            "email",
            "ATS Score",
            "Job Match",
            "Final Score",
            "Matched Skills",
            "Missing Skills",
            "status",
        ]
    ]

    ranking_df = ranking_df.rename(
        columns={
            "name": "Candidate",
            "email": "Email",
            "status": "Status",
        }
    )

    st.dataframe(
        ranking_df,
        width="stretch",
        hide_index=True,
    )


st.divider()


# ---------------------------------
# Candidate Profile
# ---------------------------------
st.subheader("👤 Candidate Profile")


if filtered_df.empty:
    st.info(
        "Candidate details will appear when at least "
        "one candidate matches the filters."
    )

else:
    candidate_options = {
        (f"Rank {row['rank']} — " f"{row['name']} — " f"{row['email']}"): row["id"]
        for _, row in filtered_df.iterrows()
    }

    selected_candidate_label = st.selectbox(
        "Select Candidate",
        options=list(candidate_options.keys()),
    )

    selected_candidate_id = candidate_options[selected_candidate_label]

    candidate = filtered_df[filtered_df["id"] == selected_candidate_id].iloc[0]

    profile_col1, profile_col2 = st.columns(2)

    with profile_col1:
        st.markdown("#### Personal Information")

        st.write(f"**Name:** {candidate['name']}")

        st.write(f"**Email:** {candidate['email']}")

        st.write(f"**Phone:** " f"{candidate.get('phone') or 'Not Available'}")

        st.write(f"**Current Status:** " f"{candidate.get('status') or 'Under Review'}")

    with profile_col2:
        st.markdown("#### Ranking Information")

        st.metric(
            "Final Recruiter Score",
            f"{float(candidate['combined_score']):.1f}%",
        )

        st.metric(
            "Job Match",
            f"{float(candidate['match_score']):.1f}%",
        )

        st.metric(
            "ATS Score",
            f"{float(candidate['ats_score'] or 0):.1f}%",
        )

    st.markdown("#### 💻 Candidate Skills")

    candidate_skills = normalize_skills(candidate["skills"])

    if candidate_skills:
        st.write(" • ".join(candidate_skills))
    else:
        st.write("No candidate skills available.")

    skill_col1, skill_col2 = st.columns(2)

    with skill_col1:
        st.success("✅ Matched Skills")

        matched_skills = normalize_skills(candidate["matched_skills"])

        if matched_skills:
            for skill in matched_skills:
                st.write("✔", skill)
        else:
            st.write("No matched skills.")

    with skill_col2:
        st.warning("⚠️ Missing Skills")

        missing_skills = normalize_skills(candidate["missing_skills"])

        if missing_skills:
            for skill in missing_skills:
                st.write("➤", skill)
        else:
            st.write("No missing skills.")

    st.divider()

    # ---------------------------------
    # Update Candidate Status
    # ---------------------------------
    st.subheader("📌 Recruitment Decision")

    status_choices = [
        "Under Review",
        "Shortlisted",
        "Interview Scheduled",
        "Selected",
        "Rejected",
    ]

    current_status = candidate.get("status") or "Under Review"

    default_index = (
        status_choices.index(current_status) if current_status in status_choices else 0
    )

    new_status = st.selectbox(
        "Update candidate status",
        options=status_choices,
        index=default_index,
        key=f"status_{selected_candidate_id}",
    )

    if st.button(
        "💾 Save Recruitment Status",
        type="primary",
        width="stretch",
    ):
        try:
            updated = update_candidate_status(
                selected_candidate_id,
                new_status,
            )

            if updated:
                st.success("Candidate status updated successfully.")

                st.rerun()

            else:
                st.warning("Candidate record was not found.")

        except Exception as error:
            st.error(f"Unable to update candidate status: {error}")


st.divider()


# ---------------------------------
# Export Candidates
# ---------------------------------
st.subheader("📥 Export Ranked Candidates")


if filtered_df.empty:
    st.info("No candidate data is available for export.")

else:
    export_df = filtered_df.copy()

    export_df["skills"] = export_df["skills"].apply(
        lambda value: ", ".join(normalize_skills(value))
    )

    export_df["matched_skills"] = export_df["matched_skills"].apply(
        lambda value: ", ".join(normalize_skills(value))
    )

    export_df["missing_skills"] = export_df["missing_skills"].apply(
        lambda value: ", ".join(normalize_skills(value))
    )

    export_columns = [
        "rank",
        "name",
        "email",
        "phone",
        "skills",
        "ats_score",
        "match_score",
        "combined_score",
        "matched_skills",
        "missing_skills",
        "status",
    ]

    csv_data = export_df[export_columns].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Ranked Candidates",
        data=csv_data,
        file_name=(f"{selected_job.replace(' ', '_')}" "_candidate_ranking.csv"),
        mime="text/csv",
        width="stretch",
    )

    shortlisted_df = export_df[export_df["combined_score"] >= 75]

    if not shortlisted_df.empty:
        shortlisted_csv = (
            shortlisted_df[export_columns].to_csv(index=False).encode("utf-8")
        )

        st.download_button(
            label="⬇️ Download Strong Candidates Only",
            data=shortlisted_csv,
            file_name=(f"{selected_job.replace(' ', '_')}" "_strong_candidates.csv"),
            mime="text/csv",
            width="stretch",
        )

    else:
        st.info("No candidates currently have a final score of 75% or higher.")


st.caption("AI Resume Analyzer v1.0 | Recruiter Ranking Dashboard")
