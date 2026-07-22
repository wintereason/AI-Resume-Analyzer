import base64
<<<<<<< HEAD
=======
import html
>>>>>>> a1ff58d (Update UI and improve performance)
from datetime import datetime
from pathlib import Path

import streamlit as st

from auth import require_role
from resume_fetch import (
    get_all_resumes,
    get_resume_by_id,
)
from utils.activity_manager import get_candidate_activities
from utils.candidate_workflow import (
    ALLOWED_STATUSES,
    update_candidate_status,
)
from utils.email_manager import send_candidate_email
from utils.sidebar import show_sidebar
<<<<<<< HEAD
from utils.theme import (
    apply_global_styles,
    escape_html,
    page_header,
    render_candidate_avatar,
    render_skill_chips,
    render_status_badge,
    render_timeline_item,
    section_header,
)
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Candidate Profile | AI Resume Analyzer",
    page_icon="👤",
    layout="wide",
)


<<<<<<< HEAD
=======
def escape_html(value):
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
        .profile-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}.profile-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.profile-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.profile-hero p{margin:0;max-width:800px;color:rgba(255,255,255,.76);font-size:.8rem}.profile-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        div[data-testid="stSelectbox"]>div>div,div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea{background:#fff;border-color:#DDE5F0;border-radius:10px}div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:15px!important;box-shadow:0 7px 20px rgba(35,52,84,.055)}div[data-testid="stMetric"]{padding:14px;background:#fff;border:1px solid var(--line);border-radius:13px;box-shadow:0 6px 17px rgba(35,52,84,.05)}div[data-testid="stMetricValue"]{color:var(--ink);font-weight:800}
        div[data-testid="stTabs"] button{font-size:.74rem;font-weight:700;color:#667389}div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--blue)}div[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:4px;background:#fff;padding:5px;border:1px solid var(--line);border-radius:12px}div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:var(--blue)}
        .profile-skill{display:inline-block;margin:3px 4px 3px 0;padding:5px 9px;border-radius:999px;color:#215AAA;background:#EDF4FF;border:1px solid #D8E6FB;font-size:.7rem;font-weight:700}.timeline-card{padding:14px 15px;margin-bottom:9px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 5px 15px rgba(35,52,84,.045)}.timeline-title{display:flex;justify-content:space-between;gap:10px;color:var(--ink);font-size:.78rem;font-weight:800}.timeline-card p{margin:7px 0;color:#667389;font-size:.72rem}.timeline-meta{color:#8A95A8;font-size:.66rem}
        div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}div[data-testid="stButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue)}div[data-testid="stAlert"]{border-radius:12px;border-width:1px}hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.profile-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow="Talent profile"):
    st.markdown(f'<div class="profile-hero"><div><div class="eyebrow">{escape_html(eyebrow)}</div><h1>{escape_html(title)}</h1><p>{escape_html(description)}</p></div><div class="profile-icon">{escape_html(icon or "♙")}</div></div>',unsafe_allow_html=True)


def render_candidate_avatar(name,size="medium"):
    pixels={"small":36,"medium":48,"large":88}.get(size,48)
    parts=[part for part in str(name or "Candidate").split() if part]
    initials=((parts[0][0]+parts[-1][0]) if len(parts)>1 else parts[0][:2] if parts else "CA").upper()
    st.markdown(f'<div class="candidate-avatar" style="width:{pixels}px;height:{pixels}px;margin:auto;font-size:{pixels/55:.2f}rem">{escape_html(initials)}</div>',unsafe_allow_html=True)


def render_status_badge(status):
    colors={"shortlisted":"#15B878","under review":"#2466D1","interview scheduled":"#F3A536","selected":"#0F9F6E","rejected":"#E6556D"}
    color=colors.get(str(status).lower(),"#718096")
    st.markdown(f'<span class="status-badge" style="color:{color};background:{color}14;border-color:{color}45">{escape_html(status)}</span>',unsafe_allow_html=True)


def render_skill_chips(skills):
    if not skills: st.caption("No skills available."); return
    chips="".join(f'<span class="profile-skill">{escape_html(skill)}</span>' for skill in skills)
    st.markdown(f'<div style="line-height:2.05">{chips}</div>',unsafe_allow_html=True)


def render_timeline_item(title,description,performed_by=None,created_at=None,icon="•",accent_color="#2466D1",**_):
    st.markdown(f'<div class="timeline-card" style="border-left:3px solid {accent_color}"><div class="timeline-title"><span>{escape_html(icon)} {escape_html(title)}</span><span class="timeline-meta">{escape_html(created_at)}</span></div><p>{escape_html(description)}</p><div class="timeline-meta">{escape_html(performed_by or "System")}</div></div>',unsafe_allow_html=True)


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
# Helper Functions
# ---------------------------------
def normalize_list(value):
    if value is None:
        return []

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]

    return [str(value).strip()]


def safe_score(value):
    try:
        return float(value or 0)

    except (TypeError, ValueError):
        return 0.0


def get_score_level(score):
    if score >= 80:
        return "Excellent"

    if score >= 60:
        return "Good"

    if score >= 40:
        return "Needs Improvement"

    return "Low"


def format_datetime(value):
    if not value:
        return "Date not available"

    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %I:%M %p")

    try:
        parsed_value = datetime.fromisoformat(str(value))

        return parsed_value.strftime("%d %b %Y, %I:%M %p")

    except (TypeError, ValueError):
        return str(value)


def get_activity_icon(activity_type):
    activity_icons = {
        "resume_uploaded": "📄",
        "resume_saved": "💾",
        "ats_generated": "⭐",
        "feedback_generated": "🤖",
        "job_recommended": "💼",
        "skill_gap_generated": "📚",
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
    }

    return activity_icons.get(
        activity_type,
        "🔹",
    )


def get_activity_color(activity_type):
    activity_colors = {
        "resume_uploaded": "#3B82F6",
        "resume_saved": "#3B82F6",
        "ats_generated": "#F59E0B",
        "feedback_generated": "#8B5CF6",
        "job_recommended": "#06B6D4",
        "skill_gap_generated": "#6366F1",
        "candidate_shortlisted": "#22C55E",
        "candidate_selected": "#16A34A",
        "candidate_rejected": "#EF4444",
        "status_updated": "#F97316",
        "interview_scheduled": "#0EA5E9",
        "interview_status_updated": "#14B8A6",
        "interview_rescheduled": "#EAB308",
        "interview_deleted": "#EF4444",
        "email_sent": "#A855F7",
        "offer_sent": "#22C55E",
    }

    return activity_colors.get(
        activity_type,
        "#64748B",
    )


def display_pdf(pdf_path):
    if not pdf_path:
        st.info("No original resume PDF is linked to this candidate.")
        return

    file_path = Path(pdf_path)

    if not file_path.exists():
        st.warning(
            "The saved resume path exists in the database, "
            "but the PDF file could not be found."
        )

        st.code(str(file_path))
        return

    try:
        pdf_bytes = file_path.read_bytes()

        encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_viewer = f"""
        <iframe
            src="data:application/pdf;base64,{encoded_pdf}"
            width="100%"
            height="850"
            type="application/pdf"
            style="
                border: 1px solid rgba(148,163,184,0.25);
                border-radius: 14px;
                background: white;
            "
        ></iframe>
        """

        st.markdown(
            pdf_viewer,
            unsafe_allow_html=True,
        )

        st.download_button(
            label="⬇️ Download Original Resume",
            data=pdf_bytes,
            file_name=file_path.name,
            mime="application/pdf",
            width="stretch",
        )

    except Exception as error:
        st.error(f"Unable to display the resume PDF: {error}")


def create_timeline_report(
    candidate_name,
    activities,
):
    report_lines = [
        "AI RESUME ANALYZER - CANDIDATE ACTIVITY TIMELINE",
        "",
        f"Candidate: {candidate_name}",
        "",
    ]

    if not activities:
        report_lines.append("No activity records are available.")

        return "\n".join(report_lines)

    for index, activity in enumerate(
        activities,
        start=1,
    ):
        report_lines.extend(
            [
                (
                    f"{index}. "
                    f"{activity.get('activity_title') or 'Candidate Activity'}"
                ),
                (f"Date: " f"{format_datetime(activity.get('created_at'))}"),
                (f"Performed By: " f"{activity.get('performed_by_name') or 'System'}"),
                (
                    f"Activity Type: "
                    f"{activity.get('activity_type') or 'Not Available'}"
                ),
            ]
        )

        description = activity.get("activity_description")

        if description:
            report_lines.append(f"Description: {description}")

        old_status = activity.get("old_status")

        new_status = activity.get("new_status")

        if old_status or new_status:
            report_lines.append(
                f"Status Change: "
                f"{old_status or 'Not Set'} → "
                f"{new_status or 'Not Set'}"
            )

        report_lines.append("")

    return "\n".join(report_lines)


def get_interview_email(
    candidate_name,
    recommended_role,
):
    subject = f"Interview Invitation – {recommended_role}"

    body = f"""Dear {candidate_name},

We are pleased to invite you for an interview for the position of {recommended_role}.

Your profile has been reviewed, and we would like to discuss your skills, projects, and suitability for the role.

Please reply to this email to confirm your availability. The interview date, time, mode, and meeting details will be shared with you by the recruitment team.

Regards,
Recruitment Team
AI Resume Analyzer
"""

    return subject, body


def get_selection_email(
    candidate_name,
    recommended_role,
):
    subject = f"Selection Update – {recommended_role}"

    body = f"""Dear {candidate_name},

Congratulations!

We are pleased to inform you that you have been selected for the position of {recommended_role}.

Your profile and performance were found suitable for the role. The recruitment team will contact you shortly with the next steps and joining information.

Regards,
Recruitment Team
AI Resume Analyzer
"""

    return subject, body


def get_rejection_email(
    candidate_name,
    recommended_role,
):
    subject = f"Application Update – {recommended_role}"

    body = f"""Dear {candidate_name},

Thank you for your interest in the position of {recommended_role} and for taking the time to participate in our recruitment process.

After reviewing your profile, we have decided not to proceed with your application for this role.

We appreciate your effort and encourage you to apply for future opportunities that match your skills and experience.

Regards,
Recruitment Team
AI Resume Analyzer
"""

    return subject, body


# ---------------------------------
# Page Header
# ---------------------------------
page_header(
    title="Candidate Profile",
    description=(
        "Review candidate details, ATS performance, recruitment status, interview readiness, and activity history in one workspace."
    ),
    icon="👤",
    eyebrow="Talent Profile",
)


# ---------------------------------
# Load Candidates
# ---------------------------------
try:
    candidates = get_all_resumes()

except Exception as error:
    st.error(f"Unable to load candidates: {error}")
    st.stop()


if not candidates:
    st.info("No saved candidates are available.")
    st.stop()


candidate_options = {
    (
        f"{candidate.get('name') or 'Unknown Candidate'} — "
        f"{candidate.get('email') or 'No Email'} — "
        f"ID {candidate.get('id')}"
    ): candidate.get("id")
    for candidate in candidates
}


selected_candidate_label = st.selectbox(
    "Select Candidate",
    options=list(candidate_options.keys()),
    index=(
        list(candidate_options.values()).index(
            st.session_state["selected_candidate_profile_id"]
        )
        if st.session_state.get("selected_candidate_profile_id")
        in candidate_options.values()
        else 0
    ),
)


selected_candidate_id = candidate_options[selected_candidate_label]


# ---------------------------------
# Load Candidate Profile
# ---------------------------------
try:
    candidate = get_resume_by_id(selected_candidate_id)

except Exception as error:
    st.error(f"Unable to load candidate profile: {error}")
    st.stop()


if not candidate:
    st.warning("The selected candidate could not be found.")
    st.stop()


# ---------------------------------
# Candidate Values
# ---------------------------------
candidate_name = candidate.get("name") or "Unknown Candidate"

candidate_email = candidate.get("email") or "Not Available"

candidate_phone = candidate.get("phone") or "Not Available"

candidate_status = candidate.get("status") or "Under Review"

recommended_role = candidate.get("recommended_role") or "Not Assigned"

resume_file = candidate.get("resume_file") or ""

ats_score = safe_score(candidate.get("ats_score"))

skills = normalize_list(candidate.get("skills"))

education = normalize_list(candidate.get("education"))

projects = normalize_list(candidate.get("projects"))


# ---------------------------------
# Load Candidate Activities
# ---------------------------------
try:
    candidate_activities = get_candidate_activities(selected_candidate_id)

except Exception as error:
    st.warning(f"Activity timeline could not be loaded: {error}")

    candidate_activities = []


st.divider()


# ---------------------------------
# Profile Overview
# ---------------------------------
profile_left, profile_right = st.columns([1, 3])


with profile_left:
    with st.container(border=True):
        render_candidate_avatar(candidate_name, size="large")

        st.markdown(
            f"<h3 style='text-align:center;margin:0.75rem 0 0.25rem 0;'>"
            f"{escape_html(candidate_name)}</h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
<<<<<<< HEAD
            f"<p style='text-align:center;color:#94A3B8;margin:0;'>"
=======
            f"<p style='text-align:center;color:#718096;margin:0;'>"
>>>>>>> a1ff58d (Update UI and improve performance)
            f"{escape_html(recommended_role)}</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='text-align:center;margin-top:0.5rem;'>", unsafe_allow_html=True
        )
        render_status_badge(candidate_status)
        st.markdown("</div>", unsafe_allow_html=True)


with profile_right:
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("⭐ ATS Score", f"{ats_score:.1f}%")

    with metric_col2:
        st.metric("📊 ATS Level", get_score_level(ats_score))

    with metric_col3:
        st.metric("💻 Skills", len(skills))

    with metric_col4:
        st.metric("📋 Activities", len(candidate_activities))

    with st.container(border=True):
        st.markdown("### 📇 Contact Information")

        contact_col1, contact_col2 = st.columns(2)

        with contact_col1:
            st.write(f"**📧 Email:** {candidate_email}")

        with contact_col2:
            st.write(f"**📞 Phone:** {candidate_phone}")

        st.caption(
            "This profile can be used for review, interview scheduling, and recruiter communications."
        )


st.divider()


# ---------------------------------
# Main Profile Tabs
# ---------------------------------
(
    resume_tab,
    skills_tab,
    education_tab,
    projects_tab,
    recruitment_tab,
    email_tab,
    timeline_tab,
) = st.tabs(
    [
        "📄 Original Resume",
        "💻 Skills",
        "🎓 Education",
        "📁 Projects",
        "👨‍💼 Recruitment",
        "📧 Candidate Email",
        "📋 Activity Timeline",
    ]
)


# ---------------------------------
# Resume Tab
# ---------------------------------
with resume_tab:

    st.subheader("Original Resume")

    st.write("Preview or download the original PDF resume uploaded for this candidate.")

    display_pdf(resume_file)


# ---------------------------------
# Skills Tab
# ---------------------------------
with skills_tab:
    st.subheader("Candidate Skills")

    if skills:
        render_skill_chips(skills)
    else:
        st.info("No skills are available for this candidate.")


# ---------------------------------
# Education Tab
# ---------------------------------
with education_tab:

    st.subheader("Education Details")

    if education:

        for item in education:

            with st.container(border=True):
                st.write(f"🎓 {item}")

    else:
        st.info("No education information is available.")


# ---------------------------------
# Projects Tab
# ---------------------------------
with projects_tab:

    st.subheader("Candidate Projects")

    if projects:

        for index, project in enumerate(
            projects,
            start=1,
        ):

            with st.container(border=True):

                st.markdown(f"### 📁 Project {index}")

                st.write(project)

    else:
        st.info("No project information is available.")


# ---------------------------------
# Recruitment Tab
# ---------------------------------
with recruitment_tab:

    st.subheader("Recruitment Information")

    recruitment_col1, recruitment_col2 = st.columns(2)

    with recruitment_col1:

        with st.container(border=True):

            st.markdown("### 🎯 Recommended Role")

            st.success(recommended_role)

    with recruitment_col2:

        with st.container(border=True):

            st.markdown("### 📌 Current Status")

            st.info(candidate_status)

    st.markdown("### ⭐ ATS Performance")

    st.progress(
        max(
            0,
            min(ats_score, 100),
        )
        / 100
    )

    if ats_score >= 80:
        st.success("This resume has strong ATS compatibility.")

    elif ats_score >= 60:
        st.warning("This resume has moderate ATS compatibility.")

    else:
        st.error("This resume requires ATS improvement.")

    st.divider()

    # ---------------------------------
    # Candidate Workflow
    # ---------------------------------
    st.subheader("📌 Candidate Decision Workflow")

    st.write(
        "Update the candidate’s recruitment status. "
        "Every change is recorded in the activity timeline."
    )

    decision_note = st.text_area(
        "Decision Note",
        placeholder=(
            "Example: Strong Python and SQL skills. Move to the technical interview."
        ),
        key=f"decision_note_{selected_candidate_id}",
    )

    status_columns = st.columns(4)

    with status_columns[0]:
        shortlist_clicked = st.button(
            "✅ Shortlist",
            width="stretch",
            disabled=(candidate_status == "Shortlisted"),
            key=f"shortlist_{selected_candidate_id}",
        )

    with status_columns[1]:
        review_clicked = st.button(
            "🔍 Review",
            width="stretch",
            disabled=(candidate_status == "Under Review"),
            key=f"review_{selected_candidate_id}",
        )

    with status_columns[2]:
        select_clicked = st.button(
            "🎉 Select",
            width="stretch",
            type="primary",
            disabled=(candidate_status == "Selected"),
            key=f"select_{selected_candidate_id}",
        )

    with status_columns[3]:
        reject_clicked = st.button(
            "❌ Reject",
            width="stretch",
            disabled=(candidate_status == "Rejected"),
            key=f"reject_{selected_candidate_id}",
        )

    requested_status = None

    if shortlist_clicked:
        requested_status = "Shortlisted"

    elif review_clicked:
        requested_status = "Under Review"

    elif select_clicked:
        requested_status = "Selected"

    elif reject_clicked:
        requested_status = "Rejected"

    if requested_status:

        try:
            updated = update_candidate_status(
                candidate_id=selected_candidate_id,
                new_status=requested_status,
                performed_by=st.session_state.get("user_id"),
                note=decision_note,
            )

            if updated:
                st.success(f"Candidate status changed to {requested_status}.")

                st.rerun()

            else:
                st.info("No status change was required.")

        except Exception as error:
            st.error(f"Unable to update candidate status: {error}")

    with st.expander("⚙️ Advanced Status Update"):

        current_status_index = (
            ALLOWED_STATUSES.index(candidate_status)
            if candidate_status in ALLOWED_STATUSES
            else 1
        )

        manual_status = st.selectbox(
            "Choose Candidate Status",
            options=ALLOWED_STATUSES,
            index=current_status_index,
            key=f"manual_status_{selected_candidate_id}",
        )

        manual_note = st.text_area(
            "Status Update Note",
            key=f"manual_note_{selected_candidate_id}",
        )

        if st.button(
            "💾 Save Status",
            width="stretch",
            key=f"save_manual_status_{selected_candidate_id}",
        ):

            try:
                updated = update_candidate_status(
                    candidate_id=selected_candidate_id,
                    new_status=manual_status,
                    performed_by=st.session_state.get("user_id"),
                    note=manual_note,
                )

                if updated:
                    st.success("Candidate status updated successfully.")

                    st.rerun()

                else:
                    st.info("No status change was required.")

            except Exception as error:
                st.error(f"Unable to update status: {error}")


# ---------------------------------
# Candidate Email Tab
# ---------------------------------
with email_tab:

    st.subheader("📧 Candidate Email Workflow")

    st.write(
        "Generate, review, and send recruitment emails " "to the selected candidate."
    )

    valid_candidate_email = (
        candidate_email
        and candidate_email != "Not Available"
        and "@" in candidate_email
    )

    if not valid_candidate_email:
        st.warning("This candidate does not have a valid email address.")

    else:
        st.info(f"Recipient: {candidate_email}")

        email_type = st.selectbox(
            "Choose Email Type",
            options=[
                "Interview Invitation",
                "Selection Email",
                "Rejection Email",
            ],
            key=f"email_type_{selected_candidate_id}",
        )

        if email_type == "Interview Invitation":
            default_subject, default_body = get_interview_email(
                candidate_name,
                recommended_role,
            )
            internal_email_type = "interview"

        elif email_type == "Selection Email":
            default_subject, default_body = get_selection_email(
                candidate_name,
                recommended_role,
            )
            internal_email_type = "selection"

        else:
            default_subject, default_body = get_rejection_email(
                candidate_name,
                recommended_role,
            )
            internal_email_type = "rejection"

        subject_key = f"email_subject_{selected_candidate_id}_" f"{internal_email_type}"

        body_key = f"email_body_{selected_candidate_id}_" f"{internal_email_type}"

        if subject_key not in st.session_state:
            st.session_state[subject_key] = default_subject

        if body_key not in st.session_state:
            st.session_state[body_key] = default_body

        email_subject = st.text_input(
            "Email Subject",
            key=subject_key,
        )

        email_body = st.text_area(
            "Email Message",
            height=350,
            key=body_key,
        )

        st.caption(
            "Review the recipient, subject, and message " "carefully before sending."
        )

        confirm_send = st.checkbox(
            "I confirm that this email is ready to send.",
            key=(f"confirm_email_{selected_candidate_id}_" f"{internal_email_type}"),
        )

        if st.button(
            "📧 Send Candidate Email",
            type="primary",
            width="stretch",
            disabled=not confirm_send,
            key=(f"send_email_{selected_candidate_id}_" f"{internal_email_type}"),
        ):
            try:
                with st.spinner("Sending candidate email..."):
                    send_candidate_email(
                        candidate_id=selected_candidate_id,
                        recipient_email=candidate_email,
                        subject=email_subject,
                        body=email_body,
                        performed_by=st.session_state.get("user_id"),
                        email_type=internal_email_type,
                    )

                st.success(f"Email sent successfully to " f"{candidate_email}.")

                st.rerun()

            except Exception as error:
                st.error(f"Unable to send email: {error}")


# ---------------------------------
# Activity Timeline Tab
# ---------------------------------
with timeline_tab:

    st.subheader("Candidate Activity Timeline")

    st.write("Review the candidate’s complete recruitment history.")

    if not candidate_activities:

        st.info("No activity records are available for this candidate.")

    else:

        for activity in candidate_activities:

            activity_type = activity.get("activity_type") or "general_activity"

            activity_icon = get_activity_icon(activity_type)

            activity_color = get_activity_color(activity_type)

            activity_title = activity.get("activity_title") or "Candidate Activity"

            activity_description = (
                activity.get("activity_description") or "No additional description."
            )

            performed_by = activity.get("performed_by_name") or "System"

            performed_by_role = activity.get("performed_by_role") or "Automated Process"

            activity_date = format_datetime(activity.get("created_at"))

            old_status = activity.get("old_status")

            new_status = activity.get("new_status")

            render_timeline_item(
                title=activity_title,
                description=activity_description,
                performed_by=f"{performed_by} ({performed_by_role})",
                created_at=activity_date,
                icon=activity_icon,
                accent_color=activity_color,
            )

            if old_status or new_status:

                status_col1, status_col2, status_col3 = st.columns([1, 0.25, 1])

                with status_col1:
                    st.info(f"Previous: {old_status or 'Not Set'}")

                with status_col2:
                    st.markdown(
                        "<h3 style='text-align:center;'>→</h3>",
                        unsafe_allow_html=True,
                    )

                with status_col3:
                    st.success(f"New: {new_status or 'Not Set'}")

        timeline_report = create_timeline_report(
            candidate_name,
            candidate_activities,
        )

        st.download_button(
            label="⬇️ Download Activity Timeline",
            data=timeline_report,
            file_name=f"{candidate_name.replace(' ', '_')}_activity_timeline.txt",
            mime="text/plain",
            width="stretch",
        )


st.divider()


# ---------------------------------
# Recruiter Summary
# ---------------------------------
st.subheader("🤖 Recruiter Profile Summary")


top_skills = skills[:5]

skills_text = (
    ", ".join(top_skills) if top_skills else "no clearly identified technical skills"
)


summary = (
    f"{candidate_name} has an ATS score of "
    f"{ats_score:.1f}% and is currently marked as "
    f"{candidate_status}. The candidate is recommended "
    f"for the role of {recommended_role}. Key identified "
    f"skills include {skills_text}. The profile contains "
    f"{len(projects)} project(s), "
    f"{len(education)} education entry or entries, and "
    f"{len(candidate_activities)} recruitment activities."
)


st.info(summary)


st.divider()


# ---------------------------------
# Export Candidate Profile
# ---------------------------------
st.subheader("📥 Export Candidate Profile")


profile_report_lines = [
    "AI RESUME ANALYZER - CANDIDATE PROFILE",
    "",
    f"Candidate: {candidate_name}",
    f"Email: {candidate_email}",
    f"Phone: {candidate_phone}",
    f"ATS Score: {ats_score:.1f}%",
    f"Recommended Role: {recommended_role}",
    f"Recruitment Status: {candidate_status}",
    f"Resume File: {resume_file or 'Not Available'}",
    "",
    "Skills:",
    ", ".join(skills) if skills else "Not Available",
    "",
    "Education:",
    ", ".join(education) if education else "Not Available",
    "",
    "Projects:",
    ", ".join(projects) if projects else "Not Available",
    "",
    "Recruiter Summary:",
    summary,
    "",
    "Activity Timeline:",
]


if candidate_activities:

    for index, activity in enumerate(
        candidate_activities,
        start=1,
    ):
        profile_report_lines.append(
            (
                f"{index}. "
                f"{activity.get('activity_title') or 'Candidate Activity'}"
                f" — "
                f"{format_datetime(activity.get('created_at'))}"
            )
        )

else:
    profile_report_lines.append("No activity records available.")


profile_report = "\n".join(profile_report_lines)


safe_candidate_name = candidate_name.replace(" ", "_").replace("/", "_")


st.download_button(
    label="⬇️ Download Complete Candidate Profile",
    data=profile_report,
    file_name=f"{safe_candidate_name}_profile.txt",
    mime="text/plain",
    width="stretch",
)


st.caption(
    "AI Resume Analyzer v1.0 | Candidate Profile, Resume Preview, Hiring Workflow and Email"
)
