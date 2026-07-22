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
from database import get_connection
from utils.recruiter_matching import (
    get_job_skills,
    match_candidates,
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
    page_title="Recruiter Dashboard | AI Resume Analyzer",
    page_icon="👨‍💼",
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
        header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1500px;padding:1rem 1.4rem 2.5rem}
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
        .recruiter-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}
        .recruiter-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.recruiter-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.recruiter-hero p{margin:0;max-width:790px;color:rgba(255,255,255,.76);font-size:.8rem}
        .recruiter-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .rank-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;box-shadow:0 9px 21px rgba(39,55,93,.12)}.rank-metric:after{content:"";position:absolute;width:90px;height:90px;right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}
        .metric-icon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}.metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;font-size:1.48rem;font-weight:800;line-height:1}.metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}
        .skill-chip{display:inline-block;margin:3px 4px 3px 0;padding:5px 9px;border-radius:999px;color:#215AAA;background:#EDF4FF;border:1px solid #D8E6FB;font-size:.7rem;font-weight:700}
        .empty-state{text-align:center;padding:42px 22px;border:1px dashed #C8D3E3;border-radius:15px;background:#fff}.empty-state .empty-icon{font-size:1.6rem}.empty-state h4{margin:9px 0 3px}.empty-state p{margin:0;font-size:.76rem}
        div[data-testid="stSelectbox"]>div>div,div[data-testid="stTextInput"] input{background:#fff;border-color:#DDE5F0;border-radius:10px}div[data-testid="stSlider"]{padding:3px}.stSlider [data-baseweb="slider"] div[role="slider"]{background:var(--blue)}
        div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 7px 20px rgba(35,52,84,.055);overflow:hidden}div[data-testid="stDataFrame"] [role="columnheader"]{background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stMetric"]{padding:14px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 17px rgba(35,52,84,.05)}div[data-testid="stMetricValue"]{color:var(--ink);font-weight:800}
        div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}div[data-testid="stButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue)}
        div[data-testid="stAlert"]{border-radius:12px;border-width:1px}hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.recruiter-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Recruiter intelligence"):
    st.markdown(
        f'<div class="recruiter-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></div><div class="recruiter-icon">{escape(icon or "♙")}</div></div>',
        unsafe_allow_html=True,
    )


def render_kpi_row(cards):
    colors=[("#5147C6","#6655D5"),("#0879B9","#1598D0"),("#0797AB","#09B8C4"),("#13A875","#1BC58A")]
    columns=st.columns(len(cards))
    for index,(column,card) in enumerate(zip(columns,cards)):
        start,end=colors[index % len(colors)]
        with column:
            st.markdown(
                f'<div class="rank-metric" style="background:linear-gradient(135deg,{start},{end})"><div class="metric-icon">{escape(card.get("icon"))}</div>'
                f'<div class="metric-label">{escape(card.get("label"))}</div><div class="metric-value">{escape(card.get("value"))}</div><div class="metric-note">Updated ranking data</div></div>',
                unsafe_allow_html=True,
            )


def render_skill_chips(skills):
    if not skills:
        st.caption("No skills available.")
        return
    chips="".join(f'<span class="skill-chip">{escape(skill)}</span>' for skill in skills)
    st.markdown(f'<div style="line-height:2.05">{chips}</div>',unsafe_allow_html=True)


def render_empty_state(title,message,icon="⌕"):
    st.markdown(f'<div class="empty-state"><div class="empty-icon">{escape(icon)}</div><h4>{escape(title)}</h4><p>{escape(message)}</p></div>',unsafe_allow_html=True)


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

<<<<<<< HEAD
st.write(" • ".join(required_skills))
=======
render_skill_chips(required_skills)
>>>>>>> a1ff58d (Update UI and improve performance)

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
<<<<<<< HEAD
        st.write(" • ".join(candidate_skills))
=======
        render_skill_chips(candidate_skills)
>>>>>>> a1ff58d (Update UI and improve performance)
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
