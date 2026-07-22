import pandas as pd
import streamlit as st

from auth import require_login
from utils.ai_assistant import answer_question
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    section_header,
)

st.set_page_config(
    page_title="Local Recruiter Assistant | AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
)

apply_global_styles()
require_login()
show_sidebar()

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
