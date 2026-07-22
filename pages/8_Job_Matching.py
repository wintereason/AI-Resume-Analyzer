<<<<<<< HEAD
import pandas as pd
import streamlit as st

from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    render_kpi_row,
    section_header,
)
=======
import html

import pandas as pd
import streamlit as st

>>>>>>> a1ff58d (Update UI and improve performance)
from auth import require_login
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

# ---------------------------------
# Page Configuration
# Must be the first Streamlit command
# ---------------------------------
st.set_page_config(
    page_title="Job Matching | AI Resume Analyzer",
    page_icon="🎯",
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
        .matching-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}
        .matching-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.matching-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.matching-hero p{margin:0;max-width:790px;color:rgba(255,255,255,.76);font-size:.8rem}
        .matching-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .match-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;box-shadow:0 9px 21px rgba(39,55,93,.12)}.match-metric:after{content:"";position:absolute;width:90px;height:90px;right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}
        .metric-icon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}.metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;font-size:1.48rem;font-weight:800;line-height:1}.metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}
        .skill-chip{display:inline-block;margin:3px 4px 3px 0;padding:5px 9px;border-radius:999px;color:#215AAA;background:#EDF4FF;border:1px solid #D8E6FB;font-size:.7rem;font-weight:700}
        .empty-state{text-align:center;padding:42px 22px;border:1px dashed #C8D3E3;border-radius:15px;background:#fff}.empty-state .empty-icon{font-size:1.6rem}.empty-state h4{margin:9px 0 3px}.empty-state p{margin:0;font-size:.76rem}
        div[data-testid="stSelectbox"]>div>div,div[data-testid="stTextInput"] input{background:#fff;border-color:#DDE5F0;border-radius:10px}div[data-testid="stSlider"]{padding:3px}.stSlider [data-baseweb="slider"] div[role="slider"]{background:var(--blue)}
        div[data-testid="stMetric"]{padding:14px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 17px rgba(35,52,84,.05)}div[data-testid="stMetricValue"]{color:var(--ink);font-weight:800}
        div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 7px 20px rgba(35,52,84,.055);overflow:hidden}div[data-testid="stDataFrame"] [role="columnheader"]{background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stAlert"]{border-radius:12px;border-width:1px}div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700;background:var(--blue);color:#fff}
        hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.matching-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Candidate matching"):
    st.markdown(
        f'<div class="matching-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></div><div class="matching-icon">{escape(icon or "◇")}</div></div>',
        unsafe_allow_html=True,
    )


def metric_card(label,value,icon,start,end,note):
    st.markdown(
        f'<div class="match-metric" style="background:linear-gradient(135deg,{start},{end})"><div class="metric-icon">{escape(icon)}</div>'
        f'<div class="metric-label">{escape(label)}</div><div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>',
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
    title="Job Matching",
    description=(
        "Select a job role, rank candidates by required skills, "
        "and compare candidates side by side."
    ),
    icon="🎯",
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


def normalize_skills(value):
    if value is None:
        return []

    if isinstance(value, str):
        return [skill.strip() for skill in value.split(",") if skill.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(skill).strip() for skill in value if str(skill).strip()]

    return [str(value).strip()]


def safe_float(value):
    try:
        return float(value or 0)

    except (TypeError, ValueError):
        return 0.0


def calculate_final_score(match_score, ats_score):
    """
    Final score:
    70% job-skill match
    30% ATS score
    """

    return round(
        safe_float(match_score) * 0.70 + safe_float(ats_score) * 0.30,
        2,
    )


def get_candidate_level(score):
    if score >= 85:
        return "Excellent Match"

    if score >= 70:
        return "Strong Match"

    if score >= 50:
        return "Moderate Match"

    return "Low Match"


def display_skill_list(skills, empty_message):
    clean_skills = normalize_skills(skills)

    if clean_skills:
        for skill in clean_skills:
            st.write("•", skill)

    else:
        st.write(empty_message)


# ---------------------------------
# Load Job Roles
# ---------------------------------
try:
    jobs = get_job_roles()

except Exception as error:
    st.error(f"Unable to load job roles: {error}")
    st.stop()


if not jobs:
    st.warning("No job roles are available in the database.")
    st.stop()


job_options = {job["job_title"]: job["job_role_id"] for job in jobs}


selected_job = st.selectbox(
    "Select Job Role",
    options=list(job_options.keys()),
)


selected_job_id = job_options[selected_job]


# ---------------------------------
# Required Job Skills
# ---------------------------------
try:
    required_skills = get_job_skills(selected_job_id)

except Exception as error:
    st.error(f"Unable to load required job skills: {error}")
    st.stop()


required_skills = normalize_skills(required_skills)


st.subheader("💼 Job Requirements")


job_col1, job_col2 = st.columns([2, 1])


with job_col1:
    st.markdown("#### Required Skills")

    if required_skills:
<<<<<<< HEAD
        st.write(" • ".join(required_skills))
=======
        render_skill_chips(required_skills)
>>>>>>> a1ff58d (Update UI and improve performance)

    else:
        st.warning("No required skills are assigned to this job role.")


with job_col2:
    st.metric(
        "Required Skills",
        len(required_skills),
    )


if not required_skills:
    st.stop()


st.divider()


# ---------------------------------
# Match Candidates
# ---------------------------------
try:
    candidates = match_candidates(required_skills)

except Exception as error:
    st.error(f"Unable to match candidates: {error}")
    st.stop()


if not candidates:
    st.info("No saved candidates are available for matching.")
    st.stop()


# ---------------------------------
# Calculate Final Scores and Ranking
# ---------------------------------
for candidate in candidates:
    candidate["final_score"] = calculate_final_score(
        candidate.get("match_score"),
        candidate.get("ats_score"),
    )

    candidate["match_level"] = get_candidate_level(candidate["final_score"])


candidates.sort(
    key=lambda candidate: candidate["final_score"],
    reverse=True,
)


for rank, candidate in enumerate(
    candidates,
    start=1,
):
    candidate["rank"] = rank


candidate_df = pd.DataFrame(candidates)


# ---------------------------------
# Summary Metrics
# ---------------------------------
total_candidates = len(candidate_df)

average_match = (
    pd.to_numeric(
        candidate_df["match_score"],
        errors="coerce",
    )
    .fillna(0)
    .mean()
)

highest_match = (
    pd.to_numeric(
        candidate_df["match_score"],
        errors="coerce",
    )
    .fillna(0)
    .max()
)

strong_candidates = len(candidate_df[candidate_df["final_score"] >= 70])


metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)


with metric_col1:
<<<<<<< HEAD
    st.metric(
        "👥 Candidates",
        total_candidates,
    )


with metric_col2:
    st.metric(
        "🎯 Average Match",
        f"{average_match:.1f}%",
    )


with metric_col3:
    st.metric(
        "🏆 Highest Match",
        f"{highest_match:.1f}%",
    )


with metric_col4:
    st.metric(
        "✅ Strong Candidates",
        strong_candidates,
    )
=======
    metric_card("Candidates",total_candidates,"♙","#5147C6","#6655D5","Available for this role")


with metric_col2:
    metric_card("Average Match",f"{average_match:.1f}%","◎","#0879B9","#1598D0","Mean skill compatibility")


with metric_col3:
    metric_card("Highest Match",f"{highest_match:.1f}%","↑","#0797AB","#09B8C4","Best skill alignment")


with metric_col4:
    metric_card("Strong Candidates",strong_candidates,"✓","#13A875","#1BC58A","Final score of 70%+")
>>>>>>> a1ff58d (Update UI and improve performance)


st.divider()


# ---------------------------------
# Filters
# ---------------------------------
st.subheader("🔍 Candidate Filters")


filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])


with filter_col1:
    search_text = st.text_input(
        "Search candidate",
        placeholder="Search by name, email, or skill",
    )


with filter_col2:
    minimum_match = st.slider(
        "Minimum Skill Match",
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


filtered_df = candidate_df.copy()


if search_text:
    search_value = search_text.strip().lower()

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
            lambda value: search_value in ", ".join(normalize_skills(value)).lower()
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


st.caption(f"Showing {len(filtered_df)} of " f"{len(candidate_df)} candidates")


st.divider()


# ---------------------------------
# Candidate Ranking Table
# ---------------------------------
st.subheader("🏆 Best Matching Candidates")


if filtered_df.empty:
    st.warning("No candidates match the selected filters.")

else:
    ranking_df = filtered_df.copy()

    ranking_df["Skills"] = ranking_df["skills"].apply(
        lambda skills: ", ".join(normalize_skills(skills))
    )

    ranking_df["Matched Skills"] = ranking_df["matched_skills"].apply(
        lambda skills: ", ".join(normalize_skills(skills))
    )

    ranking_df["Missing Skills"] = ranking_df["missing_skills"].apply(
        lambda skills: ", ".join(normalize_skills(skills))
    )

    ranking_df["ATS Score"] = (
        pd.to_numeric(
            ranking_df["ats_score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
    )

    ranking_df["Skill Match"] = (
        pd.to_numeric(
            ranking_df["match_score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
    )

    ranking_df["Final Score"] = (
        pd.to_numeric(
            ranking_df["final_score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
    )

    ranking_df = ranking_df[
        [
            "rank",
            "name",
            "email",
            "ATS Score",
            "Skill Match",
            "Final Score",
            "match_level",
            "Matched Skills",
            "Missing Skills",
            "status",
        ]
    ]

    ranking_df = ranking_df.rename(
        columns={
            "rank": "Rank",
            "name": "Candidate",
            "email": "Email",
            "match_level": "Match Level",
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
# Top Candidate Details
# ---------------------------------
st.subheader("🥇 Top Candidate Recommendation")


top_candidate = candidate_df.iloc[0]


top_col1, top_col2, top_col3, top_col4 = st.columns(4)


with top_col1:
    st.metric(
        "Candidate",
        top_candidate["name"],
    )


with top_col2:
    st.metric(
        "Skill Match",
        f"{safe_float(top_candidate['match_score']):.1f}%",
    )


with top_col3:
    st.metric(
        "ATS Score",
        f"{safe_float(top_candidate['ats_score']):.1f}%",
    )


with top_col4:
    st.metric(
        "Final Score",
        f"{safe_float(top_candidate['final_score']):.1f}%",
    )


st.success(
    f"Based on job-skill compatibility and ATS performance, "
    f"**{top_candidate['name']}** is currently the strongest "
    f"candidate for the **{selected_job}** role."
)


st.divider()


# ---------------------------------
# Candidate Comparison
# ---------------------------------
st.subheader("⚖️ Compare Two Candidates")


if len(candidate_df) < 2:
    st.info("At least two saved candidates are required " "for comparison.")

else:
    candidate_options = {
        (f"Rank {row['rank']} — " f"{row['name']} — {row['email']}"): row["id"]
        for _, row in candidate_df.iterrows()
    }

    comparison_col1, comparison_col2 = st.columns(2)

    with comparison_col1:
        candidate_one_label = st.selectbox(
            "Select Candidate 1",
            options=list(candidate_options.keys()),
            index=0,
        )

    with comparison_col2:
        candidate_two_label = st.selectbox(
            "Select Candidate 2",
            options=list(candidate_options.keys()),
            index=1,
        )

    candidate_one_id = candidate_options[candidate_one_label]

    candidate_two_id = candidate_options[candidate_two_label]

    if candidate_one_id == candidate_two_id:
        st.warning("Please select two different candidates.")

    else:
        candidate_one = candidate_df[candidate_df["id"] == candidate_one_id].iloc[0]

        candidate_two = candidate_df[candidate_df["id"] == candidate_two_id].iloc[0]

        candidate_one_skills = normalize_skills(candidate_one["skills"])

        candidate_two_skills = normalize_skills(candidate_two["skills"])

        candidate_one_skill_map = {
            skill.lower(): skill for skill in candidate_one_skills
        }

        candidate_two_skill_map = {
            skill.lower(): skill for skill in candidate_two_skills
        }

        common_skill_keys = set(candidate_one_skill_map.keys()) & set(
            candidate_two_skill_map.keys()
        )

        common_skills = [
            candidate_one_skill_map[key] for key in sorted(common_skill_keys)
        ]

        candidate_one_unique = [
            skill
            for key, skill in candidate_one_skill_map.items()
            if key not in candidate_two_skill_map
        ]

        candidate_two_unique = [
            skill
            for key, skill in candidate_two_skill_map.items()
            if key not in candidate_one_skill_map
        ]

        st.markdown("### 📊 Comparison Summary")

        comparison_data = pd.DataFrame(
            {
                "Feature": [
                    "Rank",
                    "ATS Score",
                    "Job Skill Match",
                    "Final Score",
                    "Total Skills",
                    "Matched Skills",
                    "Missing Skills",
                    "Recommended Role",
                    "Current Status",
                ],
                candidate_one["name"]: [
                    candidate_one["rank"],
                    f"{safe_float(candidate_one['ats_score']):.1f}%",
                    f"{safe_float(candidate_one['match_score']):.1f}%",
                    f"{safe_float(candidate_one['final_score']):.1f}%",
                    len(candidate_one_skills),
                    len(normalize_skills(candidate_one["matched_skills"])),
                    len(normalize_skills(candidate_one["missing_skills"])),
                    candidate_one.get("recommended_role") or "Not Assigned",
                    candidate_one.get("status") or "Under Review",
                ],
                candidate_two["name"]: [
                    candidate_two["rank"],
                    f"{safe_float(candidate_two['ats_score']):.1f}%",
                    f"{safe_float(candidate_two['match_score']):.1f}%",
                    f"{safe_float(candidate_two['final_score']):.1f}%",
                    len(candidate_two_skills),
                    len(normalize_skills(candidate_two["matched_skills"])),
                    len(normalize_skills(candidate_two["missing_skills"])),
                    candidate_two.get("recommended_role") or "Not Assigned",
                    candidate_two.get("status") or "Under Review",
                ],
            }
        )

        st.dataframe(
            comparison_data,
            width="stretch",
            hide_index=True,
        )

        st.markdown("### 💻 Skill Comparison")

        skills_col1, skills_col2, skills_col3 = st.columns(3)

        with skills_col1:
            st.success("✅ Common Skills")

            display_skill_list(
                common_skills,
                "No common skills found.",
            )

        with skills_col2:
            st.info(f"🔹 {candidate_one['name']} Unique Skills")

            display_skill_list(
                candidate_one_unique,
                "No unique skills.",
            )

        with skills_col3:
            st.info(f"🔹 {candidate_two['name']} Unique Skills")

            display_skill_list(
                candidate_two_unique,
                "No unique skills.",
            )

        st.markdown("### 🎯 Matched and Missing Job Skills")

        job_skill_col1, job_skill_col2 = st.columns(2)

        with job_skill_col1:
            st.markdown(f"#### {candidate_one['name']}")

            st.success("Matched Skills")

            display_skill_list(
                candidate_one["matched_skills"],
                "No matched skills.",
            )

            st.warning("Missing Skills")

            display_skill_list(
                candidate_one["missing_skills"],
                "No missing skills.",
            )

        with job_skill_col2:
            st.markdown(f"#### {candidate_two['name']}")

            st.success("Matched Skills")

            display_skill_list(
                candidate_two["matched_skills"],
                "No matched skills.",
            )

            st.warning("Missing Skills")

            display_skill_list(
                candidate_two["missing_skills"],
                "No missing skills.",
            )

        st.divider()

        # ---------------------------------
        # Comparison Decision
        # ---------------------------------
        st.subheader("🤖 Comparison Decision")

        score_one = safe_float(candidate_one["final_score"])

        score_two = safe_float(candidate_two["final_score"])

        if score_one > score_two:
            difference = score_one - score_two

            st.success(
                f"**{candidate_one['name']}** is the stronger "
                f"candidate for the **{selected_job}** role by "
                f"**{difference:.1f} points**."
            )

        elif score_two > score_one:
            difference = score_two - score_one

            st.success(
                f"**{candidate_two['name']}** is the stronger "
                f"candidate for the **{selected_job}** role by "
                f"**{difference:.1f} points**."
            )

        else:
            st.info(
                "Both candidates currently have the same final score. "
                "The recruiter should compare project quality, "
                "communication ability, and interview performance."
            )

        # ---------------------------------
        # Download Comparison Report
        # ---------------------------------
        report_lines = [
            "AI RESUME ANALYZER - CANDIDATE COMPARISON",
            "",
            f"Target Job Role: {selected_job}",
            "",
            f"Candidate 1: {candidate_one['name']}",
            f"Email: {candidate_one['email']}",
            f"ATS Score: {safe_float(candidate_one['ats_score']):.1f}%",
            f"Job Match: {safe_float(candidate_one['match_score']):.1f}%",
            f"Final Score: {safe_float(candidate_one['final_score']):.1f}%",
            f"Matched Skills: {', '.join(normalize_skills(candidate_one['matched_skills']))}",
            f"Missing Skills: {', '.join(normalize_skills(candidate_one['missing_skills']))}",
            "",
            f"Candidate 2: {candidate_two['name']}",
            f"Email: {candidate_two['email']}",
            f"ATS Score: {safe_float(candidate_two['ats_score']):.1f}%",
            f"Job Match: {safe_float(candidate_two['match_score']):.1f}%",
            f"Final Score: {safe_float(candidate_two['final_score']):.1f}%",
            f"Matched Skills: {', '.join(normalize_skills(candidate_two['matched_skills']))}",
            f"Missing Skills: {', '.join(normalize_skills(candidate_two['missing_skills']))}",
            "",
            f"Common Skills: {', '.join(common_skills) if common_skills else 'None'}",
        ]

        comparison_report = "\n".join(report_lines)

        st.download_button(
            label="⬇️ Download Comparison Report",
            data=comparison_report,
            file_name=(
                f"{candidate_one['name'].replace(' ', '_')}_"
                f"vs_{candidate_two['name'].replace(' ', '_')}.txt"
            ),
            mime="text/plain",
            width="stretch",
        )


st.divider()


# ---------------------------------
# Export Ranking
# ---------------------------------
st.subheader("📥 Export Job Matching Results")


export_df = candidate_df.copy()


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
    "final_score",
    "matched_skills",
    "missing_skills",
    "recommended_role",
    "status",
]


export_csv = export_df[export_columns].to_csv(index=False).encode("utf-8")


st.download_button(
    label="⬇️ Download Complete Job Matching Results",
    data=export_csv,
    file_name=(f"{selected_job.replace(' ', '_')}" "_matching_results.csv"),
    mime="text/csv",
    width="stretch",
)


st.caption("AI Resume Analyzer v1.0 | " "Job Matching and Candidate Comparison")
