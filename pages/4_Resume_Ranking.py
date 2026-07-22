import pandas as pd
import streamlit as st

from auth import require_login
from utils.ranking import get_resume_ranking
from utils.sidebar import show_sidebar
from utils.theme import (
    apply_global_styles,
    page_header,
    render_empty_state,
    section_header,
)

st.set_page_config(
    page_title="Resume Ranking | AI Resume Analyzer",
    page_icon="🏆",
    layout="wide",
)

apply_global_styles()
require_login()
show_sidebar()

page_header(
    title="Resume Ranking",
    description="View candidates ranked by ATS performance.",
    icon="🏆",
)

section_header("Candidate Rankings", icon="🏆")

try:
    data = get_resume_ranking()

except Exception as error:
    st.error("Unable to load resume rankings.")
    print(f"Resume ranking error: {error}")
    st.stop()

if not data:
    render_empty_state(
        "No Resumes Found",
        "Upload and save resumes to populate the ranking table.",
        icon="📄",
    )
    st.stop()

df = pd.DataFrame(data)
df.index = df.index + 1
df.index.name = "Rank"

st.dataframe(
    df,
    width="stretch",
    hide_index=False,
)

st.caption("AI Resume Analyzer v1.0 | Resume Ranking")
