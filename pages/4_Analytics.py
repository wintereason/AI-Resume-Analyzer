<<<<<<< HEAD
=======
import html

>>>>>>> a1ff58d (Update UI and improve performance)
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
<<<<<<< HEAD
from utils.theme import (
    apply_global_styles,
    page_header,
)
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Analytics | AI Resume Analyzer",
    page_icon="📊",
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
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;--blue:#2466D1;--purple:#6846C7}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}
        header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding:1rem 1.4rem 2.5rem}
        h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}
        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
        section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}
        section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;
        border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;border-color:#E4EAF4;transform:translateX(2px)}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
        .sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}
        .sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}.sidebar-account .meta{color:#8490A4;font-size:.66rem}
        .candidate-avatar{display:flex;align-items:center;justify-content:center;flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}
        .status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}
        .sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}
        .analytics-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;
        background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}
        .analytics-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
        .analytics-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.analytics-hero p{margin:0;max-width:780px;color:rgba(255,255,255,.76);font-size:.8rem}
        .analytics-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .analytics-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;box-shadow:0 9px 21px rgba(39,55,93,.12)}
        .analytics-metric:after{content:"";position:absolute;width:90px;height:90px;right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}
        .metric-icon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}
        .metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;font-size:1.48rem;font-weight:800;line-height:1}
        .metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}
        .stSubheader{margin-top:8px}h3{font-size:1rem!important;font-weight:800!important}
        div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:15px!important;box-shadow:0 7px 20px rgba(35,52,84,.055)}
        div[data-testid="stPlotlyChart"]{background:#fff;border-radius:12px;overflow:hidden}
        div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden}
        div[data-testid="stDataFrame"] [role="columnheader"]{background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stDownloadButton"] button{min-height:41px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}
        hr{border-color:#E7EBF2;margin:1.3rem 0}@media(max-width:850px){.analytics-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Analytics workspace"):
    st.markdown(
        f'<div class="analytics-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></div><div class="analytics-icon">{escape(icon or "⌁")}</div></div>',
        unsafe_allow_html=True,
    )


def metric_card(label, value, icon, start, end, note):
    st.markdown(
        f'<div class="analytics-metric" style="background:linear-gradient(135deg,{start},{end})">'
        f'<div class="metric-icon">{escape(icon)}</div><div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


>>>>>>> a1ff58d (Update UI and improve performance)
# ---------------------------------
# Global Styling and Authentication
# ---------------------------------
apply_global_styles()
require_login()
show_sidebar()
<<<<<<< HEAD
=======
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)


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
<<<<<<< HEAD
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
=======
    metric_card("Total resumes", total_resumes, "▤", "#5147C6", "#6655D5", "Complete candidate pool")


with metric_col2:
    metric_card("Average ATS", f"{average_ats:.1f}%", "◎", "#0879B9", "#1598D0", "Overall resume quality")


with metric_col3:
    metric_card("Highest ATS", f"{highest_ats:.1f}%", "↑", "#0797AB", "#09B8C4", "Top candidate score")


with metric_col4:
    metric_card("Lowest ATS", f"{lowest_ats:.1f}%", "↓", "#D94D83", "#ED6597", "Improvement opportunity")
>>>>>>> a1ff58d (Update UI and improve performance)


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
