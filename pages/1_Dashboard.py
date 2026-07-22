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
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


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
