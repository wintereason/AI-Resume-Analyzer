import pandas as pd
import streamlit as st

from auth import require_login
from utils.analytics import (
    get_analytics,
    get_ats_distribution,
    get_candidate_status_distribution,
    get_job_role_distribution,
    get_top_candidates,
    get_top_skills,
)
from utils.charts import (
    create_ats_distribution_chart,
    create_ats_gauge,
    create_job_role_chart,
    create_status_donut_chart,
    create_top_skills_chart,
)
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    page_header,
)

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Analytics | AI Resume Analyzer",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------
# Global Styling and Authentication
# ---------------------------------
apply_global_styles()
require_login()
show_sidebar()


# ---------------------------------
# Page Heading
# ---------------------------------
page_header(
    title="Resume Analytics Dashboard",
    description=(
        "Analyse candidate performance, ATS scores, skills, "
        "recommended roles, and recruitment status."
    ),
    icon="📊",
)


# ---------------------------------
# Load Summary Analytics
# ---------------------------------
try:
    analytics = get_analytics()

except Exception as error:
    st.error(f"Unable to load analytics summary: {error}")

    analytics = {
        "total": 0,
        "average": 0,
        "highest": 0,
        "lowest": 0,
    }


total_resumes = analytics.get("total", 0) or 0
average_ats = float(analytics.get("average", 0) or 0)
highest_ats = float(analytics.get("highest", 0) or 0)
lowest_ats = float(analytics.get("lowest", 0) or 0)


# ---------------------------------
# Analytics Metric Cards
# ---------------------------------
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)


with metric_col1:
    st.metric(
        label="📄 Total Resumes",
        value=total_resumes,
    )


with metric_col2:
    st.metric(
        label="⭐ Average ATS",
        value=f"{average_ats:.1f}%",
    )


with metric_col3:
    st.metric(
        label="🏆 Highest ATS",
        value=f"{highest_ats:.1f}%",
    )


with metric_col4:
    st.metric(
        label="📉 Lowest ATS",
        value=f"{lowest_ats:.1f}%",
    )


st.divider()


# ---------------------------------
# ATS and Recruitment Status
# ---------------------------------
st.subheader("📈 ATS and Recruitment Analytics")

ats_column1, ats_column2 = st.columns(2)


# ---------------------------------
# ATS Score Distribution
# ---------------------------------
with ats_column1:

    with st.container(border=True):

        st.markdown("#### ATS Score Distribution")

        try:
            ats_records = get_ats_distribution()

            if ats_records:

                ats_figure = create_ats_distribution_chart(ats_records)

                if ats_figure:

                    st.plotly_chart(
                        ats_figure,
                        width="stretch",
                        config={
                            "displaylogo": False,
                            "responsive": True,
                        },
                    )

            else:
                st.info("No ATS score information is available.")

        except Exception as error:
            st.error(f"Unable to load ATS distribution: {error}")


# ---------------------------------
# Candidate Status Distribution
# ---------------------------------
with ats_column2:

    with st.container(border=True):

        st.markdown("#### Recruitment Status")

        try:
            status_records = get_candidate_status_distribution()

            if status_records:

                status_figure = create_status_donut_chart(status_records)

                if status_figure:

                    st.plotly_chart(
                        status_figure,
                        width="stretch",
                        config={
                            "displaylogo": False,
                            "responsive": True,
                        },
                    )

            else:
                st.info("No candidate status information is available.")

        except Exception as error:
            st.error("Unable to load candidate status analytics: " f"{error}")


st.divider()


# ---------------------------------
# Skills and Job Roles
# ---------------------------------
st.subheader("💻 Skills and Job Role Analytics")

skills_column, roles_column = st.columns(2)


# ---------------------------------
# Top Skills
# ---------------------------------
with skills_column:

    with st.container(border=True):

        st.markdown("#### Top Skills")

        try:
            skills_records = get_top_skills(limit=10)

            if skills_records:

                skills_figure = create_top_skills_chart(skills_records)

                if skills_figure:

                    st.plotly_chart(
                        skills_figure,
                        width="stretch",
                        config={
                            "displaylogo": False,
                            "responsive": True,
                        },
                    )

            else:
                st.info("No skills information is available.")

        except Exception as error:
            st.error(f"Unable to load top skills: {error}")


# ---------------------------------
# Recommended Job Roles
# ---------------------------------
with roles_column:

    with st.container(border=True):

        st.markdown("#### Recommended Job Roles")

        try:
            role_records = get_job_role_distribution()

            if role_records:

                roles_figure = create_job_role_chart(role_records)

                if roles_figure:

                    st.plotly_chart(
                        roles_figure,
                        width="stretch",
                        config={
                            "displaylogo": False,
                            "responsive": True,
                        },
                    )

            else:
                st.info("No recommended job-role information " "is available.")

        except Exception as error:
            st.error(f"Unable to load job-role analytics: {error}")


st.divider()


# ---------------------------------
# Top Candidates
# ---------------------------------
st.subheader("🏆 Top Performing Candidates")


try:
    top_candidates = get_top_candidates(limit=10)

    if top_candidates:

        candidates_df = pd.DataFrame(top_candidates)

        candidates_df = candidates_df.rename(
            columns={
                "name": "Candidate",
                "email": "Email",
                "ats_score": "ATS Score",
                "recommended_role": "Recommended Role",
                "status": "Status",
            }
        )

        expected_columns = [
            "Candidate",
            "Email",
            "ATS Score",
            "Recommended Role",
            "Status",
        ]

        for column in expected_columns:
            if column not in candidates_df.columns:
                candidates_df[column] = "Not Available"

        candidates_df = candidates_df[expected_columns]

        candidates_df["ATS Score"] = pd.to_numeric(
            candidates_df["ATS Score"],
            errors="coerce",
        ).fillna(0)

        candidates_df["Recommended Role"] = candidates_df["Recommended Role"].fillna(
            "Not Assigned"
        )

        candidates_df["Status"] = candidates_df["Status"].fillna("Under Review")

        candidates_df["ATS Score"] = (
            candidates_df["ATS Score"].round(1).astype(str) + "%"
        )

        with st.container(border=True):

            st.dataframe(
                candidates_df,
                width="stretch",
                hide_index=True,
            )

            csv_data = candidates_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Export Top Candidates",
                data=csv_data,
                file_name="top_candidates_analytics.csv",
                mime="text/csv",
                width="stretch",
            )

    else:
        st.info("No candidate data is available.")

except Exception as error:
    st.error(f"Unable to load top candidates: {error}")


st.divider()


# ---------------------------------
# ATS Performance Indicator
# ---------------------------------
st.subheader("⭐ Overall ATS Performance")

safe_average_ats = max(
    0,
    min(average_ats, 100),
)


with st.container(border=True):

    ats_gauge = create_ats_gauge(safe_average_ats)

    st.plotly_chart(
        ats_gauge,
        width="stretch",
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )


if safe_average_ats >= 80:

    st.success("The uploaded candidate pool has excellent " "ATS compatibility.")

elif safe_average_ats >= 60:

    st.warning("The candidate pool has moderate " "ATS compatibility.")

else:

    st.error("The candidate pool currently has low " "ATS compatibility.")


st.caption("AI Resume Analyzer v1.0 | Recruitment Analytics")
