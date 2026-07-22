<<<<<<< HEAD
=======
import html

>>>>>>> a1ff58d (Update UI and improve performance)
import pandas as pd
import streamlit as st

from auth import require_login
from resume_fetch import (
    delete_resume,
    get_all_resumes,
    get_resume_by_id,
)
from utils.sidebar import show_sidebar
<<<<<<< HEAD
from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    render_kpi_row,
    render_status_badge,
    section_header,
)
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Saved Resumes | AI Resume Analyzer",
    page_icon="📁",
    layout="wide",
)


<<<<<<< HEAD
apply_global_styles()
require_login()
show_sidebar()
=======
def escape(value):
    return html.escape(str(value or ""), quote=True)


def apply_global_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;
        --blue:#2466D1;--cyan:#08AFC4;--green:#15B878;--amber:#F3A536;--red:#E6556D;--purple:#6846C7;}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}
        header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding:1rem 1.4rem 2.5rem}
        h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}

        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
        section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}
        section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;
        border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;
        border-color:#E4EAF4;transform:translateX(2px)}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;
        background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
        .sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);
        border-radius:12px;background:#F8FAFD}.sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}
        .sidebar-account .meta{color:#8490A4;font-size:.66rem}.candidate-avatar{display:flex;align-items:center;justify-content:center;
        flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}
        .status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}
        .sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;
        color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}

        .directory-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;
        border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);
        box-shadow:0 12px 28px rgba(37,78,150,.18)}.directory-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;
        font-weight:800;letter-spacing:.1em;text-transform:uppercase}.directory-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}
        .directory-hero p{margin:0;max-width:800px;color:rgba(255,255,255,.76);font-size:.8rem}.directory-icon{width:52px;height:52px;
        display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);
        border:1px solid rgba(255,255,255,.25);font-size:1.4rem}

        .directory-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;
        box-shadow:0 9px 21px rgba(39,55,93,.12)}.directory-metric:after{content:"";position:absolute;width:90px;height:90px;
        right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}.metric-icon{width:30px;height:30px;
        display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}
        .metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;
        font-size:1.48rem;font-weight:800;line-height:1}.metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}

        .section-heading{margin:21px 0 10px}.section-heading h3{margin:0;color:var(--ink);font-size:.98rem;font-weight:800}
        .section-heading p{margin:3px 0 0;color:var(--muted);font-size:.72rem}
        div[data-testid="stTextInput"] input,div[data-testid="stSelectbox"]>div>div{background:#fff;border-color:#DDE5F0;border-radius:10px}
        div[data-testid="stSlider"]{padding:2px 4px}.stSlider [data-baseweb="slider"] div[role="slider"]{background:var(--blue)}
        div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:15px;
        box-shadow:0 7px 20px rgba(35,52,84,.06);overflow:hidden}div[data-testid="stDataFrame"] [role="columnheader"]{
        background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:15px!important;
        box-shadow:0 7px 20px rgba(35,52,84,.055)}div[data-testid="stMetric"]{padding:14px;background:#F8FAFD;
        border:1px solid var(--line);border-radius:12px}div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button{
        min-height:41px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}div[data-testid="stButton"] button[kind="primary"]{
        color:#fff;background:var(--blue);border-color:var(--blue)}.empty-state{text-align:center;padding:42px 22px;border:1px dashed #C8D3E3;
        border-radius:15px;background:#fff}.empty-state .empty-icon{font-size:1.6rem}.empty-state h4{margin:9px 0 3px}.empty-state p{margin:0;font-size:.76rem}
        hr{border-color:#E7EBF2}@media(max-width:850px){.directory-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description="", icon="", eyebrow=None):
    st.markdown(
        f'<div class="directory-hero"><div><div class="eyebrow">{escape(eyebrow or "Candidate directory")}</div>'
        f'<h1>{escape(title)}</h1><p>{escape(description)}</p></div><div class="directory-icon">{escape(icon or "▤")}</div></div>',
        unsafe_allow_html=True,
    )


def section_header(title, description="", icon=""):
    prefix = f"{escape(icon)} " if icon else ""
    st.markdown(
        f'<div class="section-heading"><h3>{prefix}{escape(title)}</h3><p>{escape(description)}</p></div>',
        unsafe_allow_html=True,
    )


def render_kpi_row(cards):
    colors = [("#5147C6", "#6655D5"), ("#0879B9", "#1598D0"), ("#0797AB", "#09B8C4"), ("#13A875", "#1BC58A")]
    columns = st.columns(len(cards))
    for index, (column, card) in enumerate(zip(columns, cards)):
        start, end = colors[index % len(colors)]
        with column:
            st.markdown(
                f'<div class="directory-metric" style="background:linear-gradient(135deg,{start},{end})">'
                f'<div class="metric-icon">{escape(card.get("icon"))}</div><div class="metric-label">{escape(card.get("label"))}</div>'
                f'<div class="metric-value">{escape(card.get("value"))}</div><div class="metric-note">Live candidate data</div></div>',
                unsafe_allow_html=True,
            )


def render_status_badge(status):
    colors = {"shortlisted":"#15B878","under review":"#2466D1","review required":"#F3A536",
              "selected":"#0F9F6E","rejected":"#E6556D","interview scheduled":"#F3A536"}
    color = colors.get(str(status).lower(), "#718096")
    st.markdown(
        f'<span class="status-badge" style="color:{color};background:{color}14;border-color:{color}45">{escape(status)}</span>',
        unsafe_allow_html=True,
    )


def render_empty_state(title, message, icon="▤"):
    st.markdown(
        f'<div class="empty-state"><div class="empty-icon">{escape(icon)}</div><h4>{escape(title)}</h4><p>{escape(message)}</p></div>',
        unsafe_allow_html=True,
    )


apply_global_styles()
require_login()
show_sidebar()
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)

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
