<<<<<<< HEAD
=======
import html

>>>>>>> a1ff58d (Update UI and improve performance)
import pandas as pd
import streamlit as st

from auth import require_login
from utils.ai_assistant import answer_question
from utils.sidebar import show_sidebar
<<<<<<< HEAD
from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    section_header,
)
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

st.set_page_config(
    page_title="Local Recruiter Assistant | AI Resume Analyzer",
    page_icon="🤖",
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
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;--blue:#2466D1;--purple:#6846C7}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1450px;padding:1rem 1.4rem 2.5rem}h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}
        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;border-color:#E4EAF4;transform:translateX(2px)}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}.sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}.sidebar-account .meta{color:#8490A4;font-size:.66rem}.candidate-avatar{display:flex;align-items:center;justify-content:center;flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}.status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}.sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}
        .assistant-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#14489D 0%,#2466D1 58%,#6846C7 100%);box-shadow:0 12px 28px rgba(37,78,150,.18)}.assistant-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.assistant-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.assistant-hero p{margin:0;max-width:800px;color:rgba(255,255,255,.76);font-size:.8rem}.assistant-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .section-heading{margin:20px 0 10px}.section-heading h3{margin:0;color:var(--ink);font-size:.98rem;font-weight:800}.section-heading p{margin:3px 0 0;color:var(--muted);font-size:.72rem}.empty-state{text-align:center;padding:42px 22px;border:1px dashed #C8D3E3;border-radius:15px;background:#fff}.empty-state .empty-icon{font-size:1.6rem}.empty-state h4{margin:9px 0 3px}.empty-state p{margin:0;font-size:.76rem}
        div[data-testid="stTextInput"] input{min-height:48px;background:#fff;border-color:#DDE5F0;border-radius:12px;font-size:.86rem}div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:15px!important;box-shadow:0 7px 20px rgba(35,52,84,.055)}div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden}div[data-testid="stDataFrame"] [role="columnheader"]{background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button{min-height:41px;border-radius:10px;border:1px solid #D8E1EF;font-size:.72rem;font-weight:700}div[data-testid="stButton"] button:hover{color:var(--blue);border-color:#AEC3E5}div[data-testid="stButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue)}div[data-testid="stAlert"]{border-radius:12px;border-width:1px}hr{border-color:#E7EBF2;margin:1.3rem 0}@media(max-width:850px){.assistant-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title,description="",icon="",eyebrow="Local recruitment intelligence"):
    st.markdown(f'<div class="assistant-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></div><div class="assistant-icon">{escape(icon or "✦")}</div></div>',unsafe_allow_html=True)


def section_header(title,description="",icon=""):
    prefix=f"{escape(icon)} " if icon else ""
    st.markdown(f'<div class="section-heading"><h3>{prefix}{escape(title)}</h3><p>{escape(description)}</p></div>',unsafe_allow_html=True)


def render_empty_state(title,message,icon="✦"):
    st.markdown(f'<div class="empty-state"><div class="empty-icon">{escape(icon)}</div><h4>{escape(title)}</h4><p>{escape(message)}</p></div>',unsafe_allow_html=True)

apply_global_styles()
require_login()
show_sidebar()
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)

page_header(
    title="Local Recruiter Assistant",
    description=(
        "Ask rule-based questions about your candidate database. "
        "No paid API required — all answers are generated locally."
    ),
    icon="🤖",
)

st.info("Local Recruiter Assistant · No paid API required")

EXAMPLE_QUERIES = [
    "Show Python developers",
    "Who has the highest ATS score?",
    "Show candidates with ATS above 80",
    "Show Data Analyst candidates",
    "Show candidates missing Docker",
]

section_header("Example Queries", "Click an example to fill the question box", icon="💡")

example_cols = st.columns(len(EXAMPLE_QUERIES))

if "assistant_question" not in st.session_state:
    st.session_state["assistant_question"] = ""

if "assistant_history" not in st.session_state:
    st.session_state["assistant_history"] = []

for index, example in enumerate(EXAMPLE_QUERIES):
    with example_cols[index]:
        if st.button(example, width="stretch", key=f"example_{index}"):
            st.session_state["assistant_question"] = example

question = st.text_input(
    "Your question",
    value=st.session_state.get("assistant_question", ""),
    placeholder="Example: Show Python developers",
    key="assistant_input",
)

ask_col1, ask_col2 = st.columns([1, 4])

with ask_col1:
    ask_clicked = st.button("Ask Assistant", type="primary", width="stretch")

if ask_clicked:
    cleaned_question = question.strip()

    if not cleaned_question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching candidate database..."):
            intent, results = answer_question(cleaned_question)

        st.session_state["assistant_history"].insert(
            0,
            {
                "question": cleaned_question,
                "intent": intent,
                "results": results,
            },
        )

        st.session_state["assistant_question"] = cleaned_question
        st.rerun()

st.divider()

section_header("Conversation", "Recent questions and candidate results", icon="💬")

if not st.session_state["assistant_history"]:
    render_empty_state(
        "No Questions Yet",
        "Ask a question about your candidates to get started.",
        icon="🤖",
    )
else:
    for index, entry in enumerate(st.session_state["assistant_history"][:10]):
        intent = entry["intent"]
        results = entry["results"]
        asked_question = entry["question"]

        with st.container(border=True):
            st.markdown(f"**You:** {asked_question}")

            if intent == "unknown" or results is None:
                st.warning(
                    "This question is not supported yet. Try asking about skills, "
                    "ATS scores, job roles, or missing skills."
                )
                continue

            if intent == "highest_ats":
                if results:
                    st.success(
                        f"Highest ATS: **{results.get('name')}** — "
                        f"{float(results.get('ats_score') or 0):.1f}%"
                    )
                else:
                    render_empty_state(
                        "No Results",
                        "No candidates were found in the database.",
                        icon="📭",
                    )
                continue

            if not results:
                render_empty_state(
                    "No Matching Candidates",
                    "No candidates matched your question.",
                    icon="📭",
                )
                continue

            results_df = pd.DataFrame(results)

            display_df = results_df.rename(
                columns={
                    "name": "Candidate",
                    "email": "Email",
                    "phone": "Phone",
                    "skills": "Skills",
                    "ats_score": "ATS Score",
                    "recommended_role": "Recommended Role",
                    "status": "Status",
                }
            )

            if "ATS Score" in display_df.columns:
                display_df["ATS Score"] = (
                    pd.to_numeric(display_df["ATS Score"], errors="coerce")
                    .fillna(0)
                    .round(1)
                    .astype(str)
                    + "%"
                )

            preferred_columns = [
                "Candidate",
                "Email",
                "ATS Score",
                "Recommended Role",
                "Status",
                "Skills",
            ]

            display_columns = [
                column for column in preferred_columns if column in display_df.columns
            ]

            st.dataframe(
                display_df[display_columns],
                width="stretch",
                hide_index=True,
            )

            csv_data = results_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Export Results to CSV",
                data=csv_data,
                file_name=f"assistant_results_{index + 1}.csv",
                mime="text/csv",
                width="stretch",
                key=f"export_assistant_{index}",
            )

st.caption("AI Resume Analyzer v1.0 | Local Recruiter Assistant")
