<<<<<<< HEAD
=======
import html
>>>>>>> a1ff58d (Update UI and improve performance)
from datetime import date, datetime, time

import pandas as pd
import streamlit as st

from auth import require_role
from resume_fetch import get_all_resumes
from utils.interview_manager import (
    create_interview,
    delete_interview,
    get_all_interviews,
    get_upcoming_interviews,
    reschedule_interview,
    update_interview_status,
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
# ---------------------------------
st.set_page_config(
    page_title="Interview Scheduler | AI Resume Analyzer",
    page_icon="📅",
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
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;--blue:#2466D1;--cyan:#08AFC4;--green:#15B878;--amber:#F3A536;--purple:#6846C7;--red:#E6556D}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding:1rem 1.4rem 2.5rem}h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}
        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;border-color:#E4EAF4;transform:translateX(2px)}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}.sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}.sidebar-account .meta{color:#8490A4;font-size:.66rem}.candidate-avatar{display:flex;align-items:center;justify-content:center;flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}.status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}.sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}
        .interview-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}.interview-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.interview-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.interview-hero p{margin:0;max-width:800px;color:rgba(255,255,255,.76);font-size:.8rem}.interview-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .interview-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;box-shadow:0 9px 21px rgba(39,55,93,.12)}.interview-metric:after{content:"";position:absolute;width:90px;height:90px;right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}.metric-icon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}.metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;font-size:1.48rem;font-weight:800;line-height:1}.metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}
        div[data-testid="stForm"]{padding:20px;background:#fff;border:1px solid var(--line);border-radius:15px;box-shadow:0 7px 20px rgba(35,52,84,.055)}div[data-testid="stSelectbox"]>div>div,div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-testid="stDateInput"]>div>div,div[data-testid="stTimeInput"]>div>div{background:#fff;border-color:#DDE5F0;border-radius:10px}
        div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:15px!important;box-shadow:0 7px 20px rgba(35,52,84,.055)}div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 7px 20px rgba(35,52,84,.055);overflow:hidden}div[data-testid="stDataFrame"] [role="columnheader"]{background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button,div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}div[data-testid="stButton"] button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue)}div[data-testid="stAlert"]{border-radius:12px;border-width:1px}hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.interview-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Interview operations"):
    st.markdown(f'<div class="interview-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></div><div class="interview-icon">{escape(icon or "◷")}</div></div>',unsafe_allow_html=True)


def metric_card(label,value,icon,start,end,note):
    st.markdown(f'<div class="interview-metric" style="background:linear-gradient(135deg,{start},{end})"><div class="metric-icon">{escape(icon)}</div><div class="metric-label">{escape(label)}</div><div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>',unsafe_allow_html=True)


>>>>>>> a1ff58d (Update UI and improve performance)
# ---------------------------------
# Authentication and Styling
# ---------------------------------
apply_global_styles()
require_role(["Admin", "Recruiter"])
show_sidebar()
<<<<<<< HEAD
=======
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)


# ---------------------------------
# Page Header
# ---------------------------------
page_header(
    title="Interview Scheduler",
    description=(
        "Schedule candidate interviews, manage interview status, "
        "reschedule meetings, and review upcoming interview activity."
    ),
    icon="📅",
)


# ---------------------------------
# Helper Functions
# ---------------------------------
def safe_score(value):
    try:
        return float(value or 0)

    except (TypeError, ValueError):
        return 0.0


def format_time(value):
    if value is None:
        return "Not Available"

    if isinstance(value, str):
        return value

    try:
        return str(value)[:8]

    except Exception:
        return str(value)


def format_date(value):
    if value is None:
        return "Not Available"

    if isinstance(value, str):
        return value

    try:
        return value.strftime("%d %b %Y")

    except Exception:
        return str(value)


# ---------------------------------
# Load Candidates
# ---------------------------------
try:
    candidates = get_all_resumes()

except Exception as error:
    st.error(f"Unable to load candidates: {error}")
    st.stop()


if not candidates:
    st.info("No saved candidates are available. " "Upload and save a resume first.")
    st.stop()


# ---------------------------------
# Schedule New Interview
# ---------------------------------
st.subheader("➕ Schedule New Interview")


candidate_options = {
    (
        f"{candidate.get('name') or 'Unknown Candidate'} — "
        f"{candidate.get('email') or 'No Email'} — "
        f"ATS {safe_score(candidate.get('ats_score')):.1f}% — "
        f"ID {candidate.get('id')}"
    ): candidate
    for candidate in candidates
}


with st.form("schedule_interview_form"):

    selected_candidate_label = st.selectbox(
        "Select Candidate",
        options=list(candidate_options.keys()),
    )

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        interview_date = st.date_input(
            "Interview Date",
            value=date.today(),
            min_value=date.today(),
        )

        interview_time = st.time_input(
            "Interview Time",
            value=time(hour=10, minute=0),
        )

        interview_mode = st.selectbox(
            "Interview Mode",
            options=[
                "Online",
                "In Person",
                "Phone",
            ],
        )

    with form_col2:
        meeting_link = st.text_input(
            "Meeting Link",
            placeholder=("Example: Google Meet or Zoom link"),
            disabled=interview_mode != "Online",
        )

        location = st.text_input(
            "Interview Location",
            placeholder="Office or interview venue",
            disabled=interview_mode != "In Person",
        )

        notes = st.text_area(
            "Recruiter Notes",
            placeholder=(
                "Mention interview round, panel, "
                "skills to evaluate, or instructions."
            ),
            height=135,
        )

    submitted = st.form_submit_button(
        "📅 Schedule Interview",
        type="primary",
        width="stretch",
    )


if submitted:

    selected_candidate = candidate_options[selected_candidate_label]

    candidate_id = selected_candidate.get("id")
    scheduled_by = st.session_state.get("user_id")

    selected_datetime = datetime.combine(
        interview_date,
        interview_time,
    )

    if selected_datetime <= datetime.now():
        st.error("The interview date and time must be in the future.")

    elif interview_mode == "Online" and not meeting_link.strip():
        st.warning("Please enter the online meeting link.")

    elif interview_mode == "In Person" and not location.strip():
        st.warning("Please enter the interview location.")

    else:
        try:
            interview_id = create_interview(
                candidate_id=candidate_id,
                scheduled_by=scheduled_by,
                interview_date=interview_date,
                interview_time=interview_time,
                interview_mode=interview_mode,
                meeting_link=meeting_link,
                location=location,
                notes=notes,
            )

            st.success(
                "✅ Interview scheduled successfully. " f"Interview ID: {interview_id}"
            )

            st.rerun()

        except Exception as error:
            st.error(f"Unable to schedule interview: {error}")


st.divider()


# ---------------------------------
# Upcoming Interview Metrics
# ---------------------------------
st.subheader("📊 Interview Overview")


try:
    all_interviews = get_all_interviews()
    upcoming_interviews = get_upcoming_interviews()

except Exception as error:
    st.error(f"Unable to load interview data: {error}")
    all_interviews = []
    upcoming_interviews = []


scheduled_count = len(
    [
        interview
        for interview in all_interviews
        if interview.get("status") == "Scheduled"
    ]
)

completed_count = len(
    [
        interview
        for interview in all_interviews
        if interview.get("status") == "Completed"
    ]
)

cancelled_count = len(
    [
        interview
        for interview in all_interviews
        if interview.get("status") == "Cancelled"
    ]
)


metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)


with metric_col1:
<<<<<<< HEAD
    st.metric(
        "📅 Total Interviews",
        len(all_interviews),
    )


with metric_col2:
    st.metric(
        "⏳ Upcoming",
        len(upcoming_interviews),
    )


with metric_col3:
    st.metric(
        "✅ Completed",
        completed_count,
    )


with metric_col4:
    st.metric(
        "❌ Cancelled",
        cancelled_count,
    )
=======
    metric_card("Total Interviews",len(all_interviews),"▣","#5147C6","#6655D5","Complete interview history")


with metric_col2:
    metric_card("Upcoming",len(upcoming_interviews),"◷","#0879B9","#1598D0","Scheduled ahead")


with metric_col3:
    metric_card("Completed",completed_count,"✓","#13A875","#1BC58A","Finished interviews")


with metric_col4:
    metric_card("Cancelled",cancelled_count,"×","#D94D83","#ED6597","Cancelled sessions")
>>>>>>> a1ff58d (Update UI and improve performance)


st.divider()


# ---------------------------------
# Upcoming Interviews
# ---------------------------------
st.subheader("⏰ Upcoming Interviews")


if not upcoming_interviews:
    st.info("No upcoming interviews are currently scheduled.")

else:
    upcoming_df = pd.DataFrame(upcoming_interviews)

    display_upcoming = upcoming_df[
        [
            "interview_id",
            "candidate_name",
            "candidate_email",
            "ats_score",
            "recommended_role",
            "interview_date",
            "interview_time",
            "interview_mode",
            "status",
            "scheduled_by_name",
        ]
    ].copy()

    display_upcoming = display_upcoming.rename(
        columns={
            "interview_id": "Interview ID",
            "candidate_name": "Candidate",
            "candidate_email": "Email",
            "ats_score": "ATS Score",
            "recommended_role": "Recommended Role",
            "interview_date": "Date",
            "interview_time": "Time",
            "interview_mode": "Mode",
            "status": "Status",
            "scheduled_by_name": "Scheduled By",
        }
    )

    display_upcoming["ATS Score"] = (
        pd.to_numeric(
            display_upcoming["ATS Score"],
            errors="coerce",
        )
        .fillna(0)
        .round(1)
        .astype(str)
        + "%"
    )

    st.dataframe(
        display_upcoming,
        width="stretch",
        hide_index=True,
    )


st.divider()


# ---------------------------------
# Manage Interview
# ---------------------------------
st.subheader("⚙️ Manage Interview")


if not all_interviews:
    st.info("There are no interview records to manage.")

else:
    interview_options = {
        (
            f"ID {interview.get('interview_id')} — "
            f"{interview.get('candidate_name')} — "
            f"{format_date(interview.get('interview_date'))} — "
            f"{format_time(interview.get('interview_time'))}"
        ): interview
        for interview in all_interviews
    }

    selected_interview_label = st.selectbox(
        "Select Interview",
        options=list(interview_options.keys()),
    )

    selected_interview = interview_options[selected_interview_label]

    interview_id = selected_interview["interview_id"]

    candidate_id = selected_interview["candidate_id"]

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        with st.container(border=True):

            st.markdown("### 👤 Candidate")

            st.write(f"**Name:** " f"{selected_interview.get('candidate_name')}")

            st.write(f"**Email:** " f"{selected_interview.get('candidate_email')}")

            st.write(
                f"**Recommended Role:** "
                f"{selected_interview.get('recommended_role')}"
            )

            st.write(
                f"**ATS Score:** "
                f"{safe_score(selected_interview.get('ats_score')):.1f}%"
            )

    with detail_col2:

        with st.container(border=True):

            st.markdown("### 📅 Interview")

            st.write(
                f"**Date:** " f"{format_date(selected_interview.get('interview_date'))}"
            )

            st.write(
                f"**Time:** " f"{format_time(selected_interview.get('interview_time'))}"
            )

            st.write(f"**Mode:** " f"{selected_interview.get('interview_mode')}")

            st.write(f"**Status:** " f"{selected_interview.get('status')}")

    if selected_interview.get("meeting_link"):
        st.write(f"**Meeting Link:** " f"{selected_interview.get('meeting_link')}")

    if selected_interview.get("location"):
        st.write(f"**Location:** " f"{selected_interview.get('location')}")

    if selected_interview.get("notes"):
        st.write(f"**Notes:** " f"{selected_interview.get('notes')}")

    st.divider()

    # ---------------------------------
    # Update Interview Status
    # ---------------------------------
    st.markdown("### 📌 Update Interview Status")

    interview_statuses = [
        "Scheduled",
        "Completed",
        "Cancelled",
        "Rescheduled",
        "Candidate Absent",
    ]

    current_status = selected_interview.get("status") or "Scheduled"

    status_index = (
        interview_statuses.index(current_status)
        if current_status in interview_statuses
        else 0
    )

    new_status = st.selectbox(
        "Interview Status",
        options=interview_statuses,
        index=status_index,
        key=f"interview_status_{interview_id}",
    )

    if st.button(
        "💾 Update Interview Status",
        type="primary",
        width="stretch",
    ):
        try:
            updated = update_interview_status(
                interview_id=interview_id,
                candidate_id=candidate_id,
                new_status=new_status,
            )

            if updated:
                st.success("Interview status updated successfully.")

                st.rerun()

            else:
                st.warning("The interview could not be updated.")

        except Exception as error:
            st.error(f"Unable to update interview status: {error}")

    st.divider()

    # ---------------------------------
    # Reschedule Interview
    # ---------------------------------
    st.markdown("### 🔁 Reschedule Interview")

    reschedule_col1, reschedule_col2 = st.columns(2)

    with reschedule_col1:
        new_interview_date = st.date_input(
            "New Interview Date",
            value=date.today(),
            min_value=date.today(),
            key=f"new_date_{interview_id}",
        )

    with reschedule_col2:
        new_interview_time = st.time_input(
            "New Interview Time",
            value=time(hour=10, minute=0),
            key=f"new_time_{interview_id}",
        )

    if st.button(
        "🔁 Reschedule Selected Interview",
        width="stretch",
    ):
        new_datetime = datetime.combine(
            new_interview_date,
            new_interview_time,
        )

        if new_datetime <= datetime.now():
            st.error("The new interview date and time " "must be in the future.")

        else:
            try:
                updated = reschedule_interview(
                    interview_id=interview_id,
                    interview_date=new_interview_date,
                    interview_time=new_interview_time,
                )

                if updated:
                    st.success("Interview rescheduled successfully.")

                    st.rerun()

                else:
                    st.warning("The interview could not be found.")

            except Exception as error:
                st.error(f"Unable to reschedule interview: {error}")

    st.divider()

    # ---------------------------------
    # Delete Interview
    # ---------------------------------
    st.markdown("### 🗑️ Delete Interview")

    delete_confirmation = st.checkbox(
        "I understand that this interview record " "will be permanently deleted.",
        key=f"delete_interview_{interview_id}",
    )

    if st.button(
        "🗑️ Delete Selected Interview",
        width="stretch",
        disabled=not delete_confirmation,
    ):
        try:
            deleted = delete_interview(interview_id)

            if deleted:
                st.success("Interview deleted successfully.")

                st.rerun()

            else:
                st.warning("The interview record could not be found.")

        except Exception as error:
            st.error(f"Unable to delete interview: {error}")


st.divider()


# ---------------------------------
# Export Interview Data
# ---------------------------------
st.subheader("📥 Export Interview Schedule")


if all_interviews:
    export_df = pd.DataFrame(all_interviews)

    csv_data = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Interview Schedule",
        data=csv_data,
        file_name="interview_schedule.csv",
        mime="text/csv",
        width="stretch",
    )

else:
    st.info("No interview data is available for export.")


st.caption("AI Resume Analyzer v1.0 | Interview Scheduling")
