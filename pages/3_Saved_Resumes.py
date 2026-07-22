import pandas as pd
import streamlit as st

from auth import require_login
from resume_fetch import (
    delete_resume,
    get_all_resumes,
    get_resume_by_id,
)
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    render_kpi_row,
    render_status_badge,
    section_header,
)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Saved Resumes | AI Resume Analyzer",
    page_icon="📁",
    layout="wide",
)


apply_global_styles()
require_login()
show_sidebar()

page_header(
    title="Saved Resumes",
    description="Search, filter, review, export, and manage your candidate pipeline from a polished recruiting workspace.",
    icon="📁",
    eyebrow="Candidate Directory",
)


# ---------------------------------
# Load Saved Resumes
# ---------------------------------
try:
    resumes = get_all_resumes()

except Exception as error:
    st.error(f"Unable to load saved resumes: {error}")
    st.stop()


if not resumes:
    render_empty_state(
        "No Saved Resumes",
        "Upload and save a resume to view candidates here.",
        icon="📁",
    )

    if st.button("Upload Resume", width="stretch", type="primary"):
        st.switch_page("pages/2_Upload_Resume.py")

    st.stop()


# ---------------------------------
# Create DataFrame
# ---------------------------------
df = pd.DataFrame(resumes)


# Add missing columns safely
expected_columns = [
    "id",
    "name",
    "email",
    "phone",
    "education",
    "skills",
    "projects",
    "ats_score",
    "recommended_role",
    "status",
]

for column in expected_columns:
    if column not in df.columns:
        df[column] = None


# Clean important columns
df["name"] = df["name"].fillna("Unknown Candidate")
df["email"] = df["email"].fillna("Not Available")
df["phone"] = df["phone"].fillna("Not Available")
df["education"] = df["education"].fillna("")
df["skills"] = df["skills"].fillna("")
df["projects"] = df["projects"].fillna("")
df["recommended_role"] = df["recommended_role"].fillna("Not Assigned")
df["status"] = df["status"].fillna("Under Review")

df["ats_score"] = pd.to_numeric(
    df["ats_score"],
    errors="coerce",
).fillna(0)


# ---------------------------------
# Summary Cards
# ---------------------------------
total_candidates = len(df)

shortlisted_candidates = len(df[df["status"].str.lower() == "shortlisted"])

average_ats = df["ats_score"].mean() if not df.empty else 0

high_score_candidates = len(df[df["ats_score"] >= 80])


render_kpi_row(
    [
        {"label": "Total Candidates", "value": total_candidates, "icon": "📄"},
        {"label": "Average ATS", "value": f"{average_ats:.1f}%", "icon": "⭐"},
        {"label": "Shortlisted", "value": shortlisted_candidates, "icon": "✅"},
        {"label": "ATS 80+", "value": high_score_candidates, "icon": "🏆"},
    ]
)


st.divider()


# ---------------------------------
# Search and Filters
# ---------------------------------
section_header("Search and Filter", "Narrow the candidate list", icon="🔍")


filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])


with filter_col1:
    search_text = st.text_input(
        "Search candidates",
        placeholder="Enter name, email, phone, skill, or job role",
    )


with filter_col2:
    status_options = sorted(
        [status for status in df["status"].dropna().unique() if str(status).strip()]
    )

    selected_status = st.selectbox(
        "Candidate Status",
        options=["All"] + status_options,
    )


with filter_col3:
    role_options = sorted(
        [
            role
            for role in df["recommended_role"].dropna().unique()
            if str(role).strip() and str(role) != "Not Assigned"
        ]
    )

    selected_role = st.selectbox(
        "Recommended Role",
        options=["All"] + role_options,
    )


with filter_col4:
    minimum_ats = st.slider(
        "Minimum ATS Score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )


# ---------------------------------
# Apply Search
# ---------------------------------
filtered_df = df.copy()


if search_text:
    search_value = search_text.strip()

    search_mask = (
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
        | filtered_df["phone"].str.contains(
            search_value,
            case=False,
            na=False,
        )
        | filtered_df["skills"].str.contains(
            search_value,
            case=False,
            na=False,
        )
        | filtered_df["recommended_role"].str.contains(
            search_value,
            case=False,
            na=False,
        )
    )

    filtered_df = filtered_df[search_mask]


# ---------------------------------
# Apply Status Filter
# ---------------------------------
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]


if selected_role != "All":
    filtered_df = filtered_df[filtered_df["recommended_role"] == selected_role]


# ---------------------------------
# Apply ATS Filter
# ---------------------------------
filtered_df = filtered_df[filtered_df["ats_score"] >= minimum_ats]


st.caption(f"Showing {len(filtered_df)} of " f"{len(df)} saved candidates")


# ---------------------------------
# Candidate Table
# ---------------------------------
section_header(
    "Candidate List",
    "A searchable talent directory for recruiter review and action",
    icon="📋",
)


if filtered_df.empty:
    render_empty_state(
        "No Matching Candidates",
        "Try adjusting your search text or filters.",
        icon="🔍",
    )

else:
    display_df = filtered_df[
        [
            "id",
            "name",
            "email",
            "phone",
            "ats_score",
            "recommended_role",
            "status",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "id": "ID",
            "name": "Candidate",
            "email": "Email",
            "phone": "Phone",
            "ats_score": "ATS Score",
            "recommended_role": "Recommended Role",
            "status": "Status",
        }
    )

    display_df["ATS Score"] = display_df["ATS Score"].apply(
        lambda score: f"{float(score):.1f}%"
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "ATS Score": st.column_config.TextColumn("ATS Score", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Recommended Role": st.column_config.TextColumn(
                "Recommended Role", width="medium"
            ),
        },
    )


# ---------------------------------
# CSV Export
# ---------------------------------
if not filtered_df.empty:
    export_columns = [
        "name",
        "email",
        "phone",
        "education",
        "skills",
        "projects",
        "ats_score",
        "recommended_role",
        "status",
    ]

    csv_data = filtered_df[export_columns].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Export Filtered Candidates to CSV",
        data=csv_data,
        file_name="saved_candidates.csv",
        mime="text/csv",
        width="stretch",
    )


st.divider()


# ---------------------------------
# Candidate Detail View
# ---------------------------------
section_header(
    "Candidate Details",
    "Inspect a selected profile and open its full recruitment workspace",
    icon="👤",
)


if filtered_df.empty:
    st.info(
        "A candidate detail view will appear when "
        "the search produces at least one result."
    )

else:
    candidate_options = {
        f"{row['name']} — {row['email']} — ID {row['id']}": row["id"]
        for _, row in filtered_df.iterrows()
    }

    selected_candidate_label = st.selectbox(
        "Select a candidate",
        options=list(candidate_options.keys()),
    )

    selected_candidate_id = candidate_options[selected_candidate_label]

    try:
        candidate = get_resume_by_id(selected_candidate_id)

    except Exception as error:
        st.error(f"Unable to load candidate details: {error}")
        candidate = None

    if candidate:
        details_col1, details_col2 = st.columns(2)

        with details_col1:
            with st.container(border=True):
                st.markdown("#### Personal Information")
                st.write(f"**Name:** {candidate.get('name') or 'Not Available'}")
                st.write(f"**Email:** {candidate.get('email') or 'Not Available'}")
                st.write(f"**Phone:** {candidate.get('phone') or 'Not Available'}")
                st.write(
                    f"**Education:** {candidate.get('education') or 'Not Available'}"
                )

        with details_col2:
            with st.container(border=True):
                st.markdown("#### Recruitment Information")
                ats_score = candidate.get("ats_score") or 0
                st.metric("ATS Score", f"{float(ats_score):.1f}%")
                st.write(
                    f"**Recommended Role:** {candidate.get('recommended_role') or 'Not Assigned'}"
                )
                st.write(f"**Status:** {candidate.get('status') or 'Under Review'}")
                render_status_badge(candidate.get("status") or "Under Review")

        if st.button(
            "Open Candidate Profile",
            width="stretch",
            key=f"open_profile_{selected_candidate_id}",
        ):
            st.session_state["selected_candidate_profile_id"] = selected_candidate_id
            st.switch_page("pages/11_Candidate_Profile.py")

        st.markdown("#### 💻 Skills")

        skills_text = candidate.get("skills") or ""

        if skills_text:
            skills_list = [
                skill.strip() for skill in skills_text.split(",") if skill.strip()
            ]

            st.write(" • ".join(skills_list))

        else:
            st.write("No skills available.")

        st.markdown("#### 📁 Projects")

        projects_text = candidate.get("projects") or ""

        if projects_text:
            projects_list = [
                project.strip()
                for project in projects_text.split(",")
                if project.strip()
            ]

            for project in projects_list:
                st.write("•", project)

        else:
            st.write("No projects available.")

        # ---------------------------------
        # Delete Candidate
        # ---------------------------------
        st.divider()
        st.markdown("#### 🗑️ Delete Candidate")

        st.warning(
            "Deleting a candidate permanently removes "
            "their saved information from the database."
        )

        confirmation = st.checkbox(
            "I understand and want to delete this candidate",
            key=f"confirm_delete_{selected_candidate_id}",
        )

        if st.button(
            "🗑️ Delete Selected Candidate",
            type="primary",
            width="stretch",
            disabled=not confirmation,
        ):
            try:
                deleted = delete_resume(selected_candidate_id)

                if deleted:
                    st.success("Candidate deleted successfully.")

                    st.rerun()

                else:
                    st.warning("The candidate could not be found.")

            except Exception as error:
                st.error(f"Unable to delete candidate: {error}")


st.caption("AI Resume Analyzer v1.0 | Candidate Management")
