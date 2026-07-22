<<<<<<< HEAD
=======
import html
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
>>>>>>> a1ff58d (Update UI and improve performance)
import streamlit as st

from auth import require_role
from dashboard_queries import (
    get_ats_distribution,
    get_average_ats,
    get_recent_candidates,
    get_status_distribution,
    get_total_resumes,
)
from utils.activity_manager import get_recent_activities
<<<<<<< HEAD
from utils.charts import (
    create_ats_distribution_chart,
    create_status_donut_chart,
)
from utils.interview_manager import get_upcoming_interviews
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    close_chart_card,
    count_status,
    render_activity_timeline,
    render_candidates_table,
    render_chart_card,
    render_empty_state,
    render_interview_card,
    render_kpi_row,
    render_page_header,
    render_section_header,
    render_top_navbar,
)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Dashboard | AI Resume Analyzer",
    page_icon="📊",
    layout="wide",
)

apply_global_styles()
require_role(["Admin", "Recruiter"])
show_sidebar()
render_top_navbar()


# ---------------------------------
# Helpers
# ---------------------------------
def safe_float(value):
=======
from utils.interview_manager import get_upcoming_interviews
from utils.sidebar import show_sidebar
from utils.ui_system import apply_ui_system


st.set_page_config(
    page_title="Recruitment Dashboard | AI Resume Analyzer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_role(["Admin", "Recruiter"])
show_sidebar()


def apply_dashboard_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --ink: #182033;
            --muted: #6f7c92;
            --line: #e5eaf3;
            --surface: #ffffff;
            --canvas: #f3f6fb;
            --blue: #2466d1;
        }

        html, body, [class*="css"] { font-family: "Inter", sans-serif; }
        .stApp { background: var(--canvas); color: var(--ink); }
        header[data-testid="stHeader"] { background: transparent; }
        .block-container { max-width: 1580px; padding: 1rem 1.35rem 2.5rem; }

        h1, h2, h3, h4, p { font-family: "Inter", sans-serif; }

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] .block-container {
            padding: 1rem .85rem 1.25rem;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] { display: none; }
        section[data-testid="stSidebar"] hr { border-color: #edf0f5; margin: .7rem 0; }
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
            min-height: 40px;
            margin: 2px 0;
            padding: 8px 10px;
            border-radius: 10px;
            color: #536078;
            font-size: .79rem;
            font-weight: 600;
            border: 1px solid transparent;
            transition: all .16s ease;
        }
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
            color: #2466d1;
            background: #f2f6fd;
            border-color: #e4eaf4;
            transform: translateX(2px);
        }
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
            color: #ffffff;
            background: linear-gradient(110deg, #1d58b8, #286cd6);
            box-shadow: 0 7px 16px rgba(36,102,209,.18);
        }
        .sidebar-nav-label {
            margin: 13px 4px 7px;
            color: #8a95a8;
            font-size: .65rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
        }
        .sidebar-account {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 11px;
            margin-bottom: 9px;
            border: 1px solid #e5eaf3;
            border-radius: 12px;
            background: #f8fafd;
        }
        .sidebar-account .name { color: #182033; font-size: .8rem; font-weight: 800; }
        .sidebar-account .meta { color: #8490a4; font-size: .66rem; }
        .candidate-avatar {
            display: flex; align-items: center; justify-content: center;
            flex: 0 0 auto; border-radius: 50%; color: #fff;
            background: linear-gradient(135deg, #2466d1, #6846c7);
            font-weight: 800;
        }
        .status-badge {
            padding: 3px 7px;
            border: 1px solid;
            border-radius: 999px;
            font-size: .62rem;
            font-weight: 800;
        }
        .sidebar-status-row { display: grid; gap: 6px; margin: 8px 3px; }
        .sidebar-status-item {
            display: flex; align-items: center; gap: 7px;
            color: #7c889c; font-size: .67rem;
        }
        .sidebar-dot { width: 7px; height: 7px; border-radius: 50%; }

        .dash-hero {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            padding: 18px 22px;
            margin-bottom: 16px;
            border-radius: 18px;
            color: #ffffff;
            background: linear-gradient(110deg, #14489d 0%, #2466d1 55%, #6047c9 100%);
            box-shadow: 0 12px 28px rgba(37, 78, 150, .18);
        }

        .dash-brand { display: flex; align-items: center; gap: 13px; }
        .dash-logo {
            width: 42px; height: 42px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            background: rgba(255,255,255,.16);
            border: 1px solid rgba(255,255,255,.25);
            font-size: 21px; font-weight: 800;
        }
        .dash-brand h1 { margin: 0; color: #fff; font-size: 1.12rem; font-weight: 800; }
        .dash-brand p { margin: 3px 0 0; color: rgba(255,255,255,.74); font-size: .76rem; }
        .dash-user { text-align: right; }
        .dash-user strong { display: block; font-size: .86rem; }
        .dash-user span { color: rgba(255,255,255,.72); font-size: .73rem; }

        .welcome-row { margin: 5px 0 14px; }
        .welcome-row .eyebrow {
            color: #2466d1; font-size: .7rem; font-weight: 800;
            letter-spacing: .1em; text-transform: uppercase;
        }
        .welcome-row h2 { margin: 4px 0 3px; color: var(--ink); font-size: 1.45rem; font-weight: 800; }
        .welcome-row p { margin: 0; color: var(--muted); font-size: .83rem; }

        .metric-card {
            min-height: 126px;
            padding: 17px 18px;
            border-radius: 16px;
            color: #fff;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 22px rgba(39, 55, 93, .13);
            transition: transform .18s ease, box-shadow .18s ease;
        }
        .metric-card:hover { transform: translateY(-2px); box-shadow: 0 14px 28px rgba(39,55,93,.18); }
        .metric-card:after {
            content: ""; position: absolute; width: 100px; height: 100px;
            border-radius: 50%; top: -50px; right: -35px;
            background: rgba(255,255,255,.16);
        }
        .metric-top { display: flex; justify-content: space-between; align-items: center; }
        .metric-label { font-size: .74rem; font-weight: 600; color: rgba(255,255,255,.82); }
        .metric-icon {
            width: 31px; height: 31px; display: flex; align-items: center; justify-content: center;
            border-radius: 9px; background: rgba(255,255,255,.17); font-size: .93rem;
        }
        .metric-value { margin-top: 12px; font-size: 1.65rem; line-height: 1; font-weight: 800; }
        .metric-foot { margin-top: 8px; font-size: .7rem; color: rgba(255,255,255,.75); }

        .panel-title { margin: 3px 0 10px; }
        .panel-title h3 { margin: 0; color: var(--ink); font-size: .92rem; font-weight: 800; }
        .panel-title p { margin: 3px 0 0; color: var(--muted); font-size: .72rem; }

        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"],
        .white-card {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 15px;
            box-shadow: 0 6px 18px rgba(35, 52, 84, .06);
            overflow: hidden;
        }
        div[data-testid="stDataFrame"] [role="columnheader"] {
            background: #f7f9fc;
            color: #59667c;
            font-weight: 700;
        }

        .side-card {
            background: #fff; border: 1px solid var(--line); border-radius: 15px;
            padding: 16px; margin-bottom: 12px;
            box-shadow: 0 6px 18px rgba(35,52,84,.06);
        }
        .side-card h4 { margin: 0 0 4px; color: var(--ink); font-size: .86rem; }
        .side-card p { margin: 0; color: var(--muted); font-size: .72rem; line-height: 1.55; }

        .activity-item {
            display: flex; gap: 10px; padding: 10px 0;
            border-bottom: 1px solid #edf0f5;
        }
        .activity-item:last-child { border-bottom: 0; }
        .activity-dot {
            width: 30px; height: 30px; flex: 0 0 30px; border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            background: #edf4ff; color: #2466d1; font-size: .82rem;
        }
        .activity-copy strong { display: block; color: var(--ink); font-size: .75rem; }
        .activity-copy span { display: block; color: var(--muted); font-size: .68rem; margin-top: 2px; }

        .mini-interview {
            padding: 11px 12px; margin-bottom: 8px; background: #fff;
            border: 1px solid var(--line); border-left: 3px solid #16b77a;
            border-radius: 11px;
        }
        .mini-interview strong { color: var(--ink); font-size: .76rem; }
        .mini-interview p { margin: 3px 0 0; color: var(--muted); font-size: .68rem; }

        div[data-testid="stButton"] button {
            border-radius: 10px; font-weight: 700; min-height: 39px;
            border: 1px solid #dbe3f0;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            background: #2466d1; border-color: #2466d1;
        }
        div[data-testid="stSelectbox"] > div > div,
        div[data-testid="stDateInput"] > div > div {
            background: #fff; border-color: #dfe5ef; border-radius: 10px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff;
            border-color: var(--line) !important;
            border-radius: 15px !important;
            box-shadow: 0 6px 18px rgba(35,52,84,.06);
        }

        .footer-note { text-align: center; color: #8994a8; font-size: .68rem; margin-top: 22px; }

        @media (max-width: 900px) {
            .block-container { padding-left: .8rem; padding-right: .8rem; }
            .dash-user { display: none; }
            .metric-card { min-height: 112px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_number(value):
>>>>>>> a1ff58d (Update UI and improve performance)
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


<<<<<<< HEAD
def format_datetime(value):
    if value is None:
        return "Not Available"

    try:
        return value.strftime("%d %b %Y, %I:%M %p")

    except AttributeError:
        return str(value)


def format_time(value):
    if value is None:
        return "Not Available"

    try:
        return str(value)[:8]

    except Exception:
        return str(value)


def get_activity_icon(activity_type):
    return {
        "resume_uploaded": "📄",
        "resume_saved": "💾",
        "candidate_shortlisted": "✅",
        "candidate_selected": "🎉",
        "candidate_rejected": "❌",
        "status_updated": "📌",
        "interview_scheduled": "📅",
        "interview_status_updated": "📝",
        "interview_rescheduled": "🔁",
        "interview_deleted": "🗑️",
        "email_sent": "📧",
        "offer_sent": "🎁",
    }.get(activity_type, "🔹")


def build_ats_insight(records):
    if not records:
        return None

    top_bucket = max(records, key=lambda item: int(item.get("resume_count", 0) or 0))
    bucket_name = top_bucket.get("score_range", "the current range")
    bucket_count = int(top_bucket.get("resume_count", 0) or 0)

    return (
        f"Most candidates currently fall within the "
        f"**{bucket_name}** ATS range ({bucket_count} resumes)."
    )


def build_status_insight(records):
    if not records:
        return None

    top_status = records[0]
    status_name = top_status.get("candidate_status", "Unknown")
    status_count = int(top_status.get("candidate_count", 0) or 0)

    return (
        f"The largest pipeline stage is **{status_name}** "
        f"with {status_count} candidate(s)."
    )


# ---------------------------------
# Page Header
# ---------------------------------
user_name = st.session_state.get("user_name") or "Recruiter"

st.markdown("<div class='dashboard-shell'>", unsafe_allow_html=True)

render_page_header(
    title=f"Welcome back, {user_name}",
    description=(
        "Monitor your hiring funnel, candidate quality, interview pipeline, and recruitment momentum from one premium workspace."
    ),
    icon="📊",
    eyebrow="Recruitment Dashboard",
)

header_col, action_col, export_col = st.columns([2.6, 1.2, 1.2])
with header_col:
    timeframe = st.selectbox(
        "Date range",
        ["Last 30 days", "Last 90 days", "Quarter to date"],
        key="dashboard_timeframe",
        label_visibility="collapsed",
    )
with action_col:
    if st.button("Upload Resume", type="primary", width="stretch"):
        st.switch_page("pages/2_Upload_Resume.py")
with export_col:
    st.button("Export Report", width="stretch")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ---------------------------------
# Load Data
# ---------------------------------
with st.spinner("Loading dashboard data..."):
    try:
        total_resumes = get_total_resumes()
        average_ats_score = get_average_ats()
        status_records = get_status_distribution()
        ats_records = get_ats_distribution()
        upcoming_interviews = get_upcoming_interviews()
        recent_activities = get_recent_activities(limit=8)
        recent_data = get_recent_candidates(limit=6)

    except Exception as error:
        st.error("Unable to load dashboard data. Please check the database connection.")
        print(f"Dashboard load error: {error}")

        total_resumes = 0
        average_ats_score = 0
        status_records = []
        ats_records = []
        upcoming_interviews = []
        recent_activities = []
        recent_data = []


average_ats_score = max(0, min(safe_float(average_ats_score), 100))
shortlisted_count = count_status(status_records, "Shortlisted")
selected_count = count_status(status_records, "Selected")


# ---------------------------------
# KPI Row
# ---------------------------------
render_kpi_row(
    [
        {
            "label": "Total Candidates",
            "value": total_resumes,
            "icon": "👥",
            "subtitle": "Saved in database",
            "trend": "Active pool",
            "trend_direction": "neutral",
        },
        {
            "label": "Average ATS",
            "value": f"{average_ats_score:.1f}%",
            "icon": "⭐",
            "subtitle": "Across all resumes",
            "trend": "↑ Strong" if average_ats_score >= 70 else "Needs lift",
            "trend_direction": "up" if average_ats_score >= 70 else "down",
        },
        {
            "label": "Shortlisted",
            "value": shortlisted_count,
            "icon": "✅",
            "subtitle": "Ready for review",
            "trend": f"{shortlisted_count} active",
            "trend_direction": "up" if shortlisted_count else "neutral",
        },
        {
            "label": "Upcoming Interviews",
            "value": len(upcoming_interviews),
            "icon": "📅",
            "subtitle": "Scheduled ahead",
            "trend": "On calendar",
            "trend_direction": "neutral",
        },
        {
            "label": "Selected Candidates",
            "value": selected_count,
            "icon": "🎉",
            "subtitle": "Hiring decisions made",
            "trend": f"{selected_count} selected",
            "trend_direction": "up" if selected_count else "neutral",
        },
    ]
)


st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ---------------------------------
# Charts: ATS Distribution + Status Donut
# ---------------------------------
render_section_header(
    "Pipeline Analytics",
    "ATS distribution and candidate status breakdown in one view",
    icon="📈",
)

chart_main, chart_side = st.columns([2, 1])

with chart_main:
    render_chart_card(
        "ATS Score Distribution",
        "How candidate resumes are spread across ATS score ranges",
    )

    try:
        if ats_records:
            ats_figure = create_ats_distribution_chart(ats_records)

            if ats_figure:
                st.plotly_chart(
                    ats_figure,
                    width="stretch",
                    config={"displaylogo": False, "responsive": True},
                )
                close_chart_card(build_ats_insight(ats_records))
            else:
                close_chart_card()
                render_empty_state(
                    "No ATS Data",
                    "Upload and save resumes to populate this chart.",
                    icon="📊",
                )
        else:
            close_chart_card()
            render_empty_state(
                "No ATS Data",
                "Upload and save resumes to populate this chart.",
                icon="📊",
            )

    except Exception as error:
        close_chart_card()
        st.error("Unable to load ATS distribution.")
        print(f"ATS chart error: {error}")


with chart_side:
    render_chart_card(
        "Candidate Status",
        "Current recruitment pipeline mix",
    )

    try:
        if status_records:
            status_figure = create_status_donut_chart(status_records)

            if status_figure:
                st.plotly_chart(
                    status_figure,
                    width="stretch",
                    config={"displaylogo": False, "responsive": True},
                )
                close_chart_card(build_status_insight(status_records))
            else:
                close_chart_card()
                render_empty_state(
                    "No Status Data",
                    "Candidate statuses will appear after resumes are saved.",
                    icon="🍩",
                )
        else:
            close_chart_card()
            render_empty_state(
                "No Status Data",
                "Candidate statuses will appear after resumes are saved.",
                icon="🍩",
            )

    except Exception as error:
        close_chart_card()
        st.error("Unable to load candidate status data.")
        print(f"Status chart error: {error}")


st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ---------------------------------
# Recent Candidates + Upcoming Interviews
# ---------------------------------
candidates_col, interviews_col = st.columns([1.2, 1])

with candidates_col:
    render_section_header(
        "Recent Candidates",
        "Latest profiles added to your talent pool",
        icon="🕒",
    )

    if recent_data:
        render_candidates_table(recent_data)

        if st.button("View All Candidates", width="stretch", type="primary"):
            st.switch_page("pages/3_Saved_Resumes.py")

    else:
        render_empty_state(
            "No Candidates Yet",
            "Upload and save a resume to populate your candidate directory.",
            icon="📄",
        )

with interviews_col:
    render_section_header(
        "Upcoming Interviews",
        "Scheduled conversations with candidates",
        icon="📅",
    )

    if upcoming_interviews:
        for interview in upcoming_interviews[:5]:
            mode = interview.get("interview_mode") or "Not Available"
            mode_icon = {"Online": "💻", "In Person": "🏢", "Phone": "📞"}.get(
                mode, "📅"
            )

            render_interview_card(
                candidate_name=interview.get("candidate_name") or "Unknown",
                role=interview.get("recommended_role") or "Not Assigned",
                interview_date=str(interview.get("interview_date") or "TBD"),
                interview_time=format_time(interview.get("interview_time")),
                mode=mode,
                status=interview.get("status") or "Scheduled",
                mode_icon=mode_icon,
            )

        if st.button("Open Interview Scheduler", width="stretch", type="primary"):
            st.switch_page("pages/12_Interview_Scheduler.py")

    else:
        render_empty_state(
            "No Interviews Scheduled",
            "Schedule interviews from the Interview Scheduler page.",
            icon="📅",
        )


st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

render_section_header(
    "Quick Actions",
    "Move between candidate operations and hiring workflows without losing momentum",
    icon="⚡",
)

action_buttons = [
    ("Upload Resume", "pages/2_Upload_Resume.py"),
    ("Browse Candidates", "pages/3_Saved_Resumes.py"),
    ("Candidate Profiles", "pages/11_Candidate_Profile.py"),
    ("Job Matching", "pages/8_Job_Matching.py"),
    ("Skill Gap Analysis", "pages/7_Skill_Gap_Analysis.py"),
    ("Interview Scheduler", "pages/12_Interview_Scheduler.py"),
    ("Full Analytics", "pages/4_Analytics.py"),
]

action_cols = st.columns(4)
for index, (label, page) in enumerate(action_buttons):
    with action_cols[index % 4]:
        if st.button(label, width="stretch", key=f"qa_{index}"):
            st.switch_page(page)

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ---------------------------------
# Recent Activity
# ---------------------------------
render_section_header(
    "Recent Recruitment Activity",
    "Latest actions across the hiring pipeline",
    icon="🔔",
)

if not recent_activities:
    render_empty_state(
        "No Activity Yet",
        "Recruitment actions will appear here as you work with candidates.",
        icon="🔔",
    )
else:
    render_activity_timeline(
        recent_activities,
        icon_resolver=get_activity_icon,
    )


st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ---------------------------------
# Quick Actions
# ---------------------------------
render_section_header(
    "Quick Actions",
    "Jump to common recruitment workflows",
    icon="⚡",
)

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("Upload Resume", width="stretch", type="primary"):
        st.switch_page("pages/2_Upload_Resume.py")

with action_col2:
    if st.button("Candidate Profiles", width="stretch"):
        st.switch_page("pages/11_Candidate_Profile.py")

with action_col3:
    if st.button("Job Matching", width="stretch"):
        st.switch_page("pages/8_Job_Matching.py")

with action_col4:
    if st.button("Full Analytics", width="stretch"):
        st.switch_page("pages/4_Analytics.py")


if st.session_state.get("user_role") == "Admin":
    if st.button("Admin User Management", width="stretch"):
        st.switch_page("pages/10_Admin_User_Management.py")


st.markdown("</div>", unsafe_allow_html=True)
st.caption("AI Resume Analyzer v1.0 | Executive Recruitment Dashboard")
=======
def safe_text(value, fallback=""):
    return html.escape(str(value if value not in (None, "") else fallback), quote=True)


def count_status(records, target):
    target = target.lower()
    for record in records or []:
        name = str(record.get("candidate_status") or record.get("status") or "").lower()
        if name == target:
            return int(record.get("candidate_count") or record.get("count") or 0)
    return 0


def metric_card(label, value, note, icon, color_start, color_end):
    st.markdown(
        f"""
        <div class="metric-card" style="background:linear-gradient(135deg,{color_start},{color_end});">
            <div class="metric-top">
                <span class="metric-label">{label}</span>
                <span class="metric-icon">{icon}</span>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_layout(figure, height=305):
    figure.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=25, b=18),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter", color="#64748B", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#182033", font_color="#FFFFFF"),
    )
    return figure


def ats_chart(records):
    labels = [str(r.get("score_range") or "Unknown") for r in records]
    values = [int(r.get("resume_count") or r.get("candidate_count") or 0) for r in records]
    figure = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(
                color=["#5948C8", "#2867D8", "#08AFC4", "#15B878", "#F3A536", "#EC5D8F"][: len(labels)],
                line=dict(color="#FFFFFF", width=1),
            ),
            text=values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Candidates: %{y}<extra></extra>",
        )
    )
    figure.update_xaxes(showgrid=False, title=None)
    figure.update_yaxes(gridcolor="#EDF1F6", zeroline=False, title=None)
    return chart_layout(figure)


def status_chart(records):
    labels = [str(r.get("candidate_status") or r.get("status") or "Unknown") for r in records]
    values = [int(r.get("candidate_count") or r.get("count") or 0) for r in records]
    figure = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=.62,
            marker=dict(colors=["#2867D8", "#08AFC4", "#15B878", "#F3A536", "#EC5D8F", "#6846C7"]),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value} candidates<extra></extra>",
        )
    )
    total = sum(values)
    figure.add_annotation(text=f"<b>{total}</b><br><span style='font-size:10px'>Candidates</span>", showarrow=False)
    return chart_layout(figure)


def activity_icon(activity_type):
    return {
        "resume_uploaded": "↥",
        "resume_saved": "✓",
        "candidate_shortlisted": "★",
        "candidate_selected": "✓",
        "candidate_rejected": "×",
        "interview_scheduled": "◷",
        "email_sent": "✉",
    }.get(activity_type, "•")


apply_dashboard_styles()
apply_ui_system()

user_name = st.session_state.get("user_name") or "Recruiter"
user_role = st.session_state.get("user_role") or "Recruiter"
safe_user_name = safe_text(user_name, "Recruiter")
safe_user_role = safe_text(user_role, "Recruiter")

st.markdown(
    f"""
    <div class="dash-hero">
        <div class="dash-brand">
            <div class="dash-logo">◈</div>
            <div><h1>AI Resume Analyzer</h1><p>Recruitment intelligence and candidate analytics</p></div>
        </div>
        <div class="dash-user"><strong>{safe_user_name}</strong><span>{safe_user_role} · Secure workspace</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    total_resumes = int(get_total_resumes() or 0)
    average_ats = max(0, min(safe_number(get_average_ats()), 100))
    status_records = get_status_distribution() or []
    ats_records = get_ats_distribution() or []
    recent_candidates = get_recent_candidates(limit=8) or []
    upcoming_interviews = get_upcoming_interviews() or []
    recent_activities = get_recent_activities(limit=6) or []
except Exception as error:
    st.error("Dashboard data could not be loaded. Please verify the MySQL connection.")
    print(f"Dashboard load error: {error}")
    total_resumes, average_ats = 0, 0
    status_records, ats_records = [], []
    recent_candidates, upcoming_interviews, recent_activities = [], [], []

shortlisted = count_status(status_records, "shortlisted")
selected = count_status(status_records, "selected")

title_col, action_col = st.columns([4.2, 1])
with title_col:
    st.markdown(
        f"""
        <div class="welcome-row">
            <div class="eyebrow">Recruitment dashboard</div>
            <h2>Welcome back, {safe_user_name}</h2>
            <p>Monitor candidate quality, interviews, and hiring progress from one workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with action_col:
    st.write("")
    if st.button("＋ Upload resume", type="primary", use_container_width=True):
        st.switch_page("pages/2_Upload_Resume.py")

metric_columns = st.columns(5)
metrics = [
    ("Total candidates", f"{total_resumes:,}", "Saved talent pool", "♙", "#5147C6", "#6655D5"),
    ("Average ATS", f"{average_ats:.1f}%", "Resume quality score", "◎", "#0879B9", "#1598D0"),
    ("Shortlisted", f"{shortlisted:,}", "Ready for next stage", "✓", "#0797AB", "#09B8C4"),
    ("Interviews", f"{len(upcoming_interviews):,}", "Upcoming schedule", "◷", "#13A875", "#1BC58A"),
    ("Selected", f"{selected:,}", "Successful decisions", "★", "#D94D83", "#ED6597"),
]
for column, metric in zip(metric_columns, metrics):
    with column:
        metric_card(*metric)

st.write("")
main_col, side_col = st.columns([4.25, 1.15], gap="medium")

with main_col:
    chart_left, chart_right = st.columns([1.75, 1])
    with chart_left:
        st.markdown('<div class="panel-title"><h3>ATS score distribution</h3><p>Candidate quality across score ranges</p></div>', unsafe_allow_html=True)
        if ats_records:
            st.plotly_chart(ats_chart(ats_records), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Upload resumes to populate ATS analytics.")

    with chart_right:
        st.markdown('<div class="panel-title"><h3>Pipeline status</h3><p>Current candidate-stage mix</p></div>', unsafe_allow_html=True)
        if status_records:
            st.plotly_chart(status_chart(status_records), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Candidate statuses will appear here.")

    st.markdown('<div class="panel-title"><h3>Recent candidates</h3><p>Latest profiles added to the talent pool</p></div>', unsafe_allow_html=True)
    if recent_candidates:
        table_rows = []
        for candidate in recent_candidates:
            table_rows.append(
                {
                    "Candidate": candidate.get("name") or "Unknown",
                    "Email": candidate.get("email") or "Not available",
                    "ATS": f"{safe_number(candidate.get('ats_score')):.1f}%",
                    "Status": candidate.get("status") or "Under Review",
                    "Recommended Role": candidate.get("recommended_role") or "Not Assigned",
                }
            )
        st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True, height=282)
    else:
        st.info("No candidates have been saved yet.")

    button_a, button_b, button_c = st.columns(3)
    with button_a:
        if st.button("View all candidates", use_container_width=True):
            st.switch_page("pages/3_Saved_Resumes.py")
    with button_b:
        if st.button("Open analytics", use_container_width=True):
            st.switch_page("pages/4_Analytics.py")
    with button_c:
        if st.button("Job matching", use_container_width=True):
            st.switch_page("pages/8_Job_Matching.py")

with side_col:
    st.markdown('<div class="panel-title"><h3>Dashboard filters</h3><p>Refine the reporting view</p></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.date_input("Reporting period", value=(date.today() - timedelta(days=30), date.today()))
        st.selectbox("Candidate status", ["All statuses", "Under Review", "Shortlisted", "Interview Scheduled", "Selected", "Rejected"])
        st.selectbox("ATS range", ["All scores", "Below 50", "50–70", "71–85", "Above 85"])

    st.markdown('<div class="panel-title"><h3>Upcoming interviews</h3><p>Next scheduled conversations</p></div>', unsafe_allow_html=True)
    if upcoming_interviews:
        for interview in upcoming_interviews[:4]:
            candidate = safe_text(interview.get("candidate_name"), "Unknown candidate")
            role = safe_text(interview.get("recommended_role"), "Role not assigned")
            day = safe_text(interview.get("interview_date"), "TBD")
            time_value = safe_text(str(interview.get("interview_time") or "")[:5], "Time TBD")
            st.markdown(
                f'<div class="mini-interview"><strong>{candidate}</strong><p>{role}<br>{day} · {time_value}</p></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No upcoming interviews.")

    if st.button("Open scheduler", use_container_width=True):
        st.switch_page("pages/12_Interview_Scheduler.py")

    st.markdown('<div class="panel-title" style="margin-top:15px"><h3>Recent activity</h3><p>Latest recruitment actions</p></div>', unsafe_allow_html=True)
    if recent_activities:
        activity_html = '<div class="side-card">'
        for item in recent_activities[:5]:
            title = safe_text(item.get("activity_title"), "Candidate activity")
            candidate = safe_text(item.get("candidate_name"), "Candidate")
            activity_html += (
                f'<div class="activity-item"><div class="activity-dot">{activity_icon(item.get("activity_type"))}</div>'
                f'<div class="activity-copy"><strong>{title}</strong><span>{candidate}</span></div></div>'
            )
        activity_html += "</div>"
        st.markdown(activity_html, unsafe_allow_html=True)
    else:
        st.caption("No recent activity.")

st.markdown('<div class="footer-note">AI Resume Analyzer · Recruitment Intelligence Dashboard</div>', unsafe_allow_html=True)
>>>>>>> a1ff58d (Update UI and improve performance)
