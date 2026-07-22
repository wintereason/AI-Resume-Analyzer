import streamlit as st

from auth import (
    initialize_auth,
    login_user,
    logout_user,
)
from utils.theme import apply_global_styles, escape_html

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Login | AI Resume Analyzer",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_auth()
apply_global_styles()


# ---------------------------------
# Already Logged In
# ---------------------------------
if st.session_state["logged_in"]:
    user_name = st.session_state.get("user_name", "User")
    user_role = st.session_state.get("user_role", "")

    st.markdown(
        f"""
        <div style="max-width:620px;margin:32px auto 12px auto;">
            <div class="login-form-card" style="text-align:center;">
                <div class="login-brand-logo" style="margin:0 auto 16px auto;">✅</div>
                <h2>Welcome back</h2>
                <p class="subtitle">
                    Signed in as <b>{escape_html(user_name)}</b>
                    ({escape_html(user_role)})
                </p>
                <div class="saas-panel-card" style="text-align:left;">
                    <h4>Access ready</h4>
                    <p class="meta">Your recruiter workspace, analytics, candidate pipeline, and scheduling tools are all available.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Open Application", type="primary", width="stretch"):
            st.switch_page("app.py")

    with col2:
        if st.button("Logout", width="stretch"):
            logout_user()
            st.rerun()

    st.stop()


# ---------------------------------
# Split Login Layout
# ---------------------------------
brand_col, form_col = st.columns([1.15, 1], gap="large")

with brand_col:
    st.markdown(
        f"""
        <div class="login-brand-panel">
            <div class="login-brand-logo">🤖</div>
            <h1>AI Resume Analyzer</h1>
            <p class="tagline">
                A professional recruitment workspace for resume screening,
                ATS scoring, candidate workflows, interviews, and hiring analytics.
            </p>

            <div class="login-feature">
                <div class="login-feature-icon">📄</div>
                <div>
                    <strong>Resume intelligence</strong>
                    <span>Parse PDFs and extract structured candidate data.</span>
                </div>
            </div>

            <div class="login-feature">
                <div class="login-feature-icon">⭐</div>
                <div>
                    <strong>ATS scoring</strong>
                    <span>Evaluate compatibility and identify skill gaps instantly.</span>
                </div>
            </div>

            <div class="login-feature">
                <div class="login-feature-icon">📅</div>
                <div>
                    <strong>Recruitment operations</strong>
                    <span>Manage interviews, workflows, and candidate communication.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with form_col:
    st.markdown(
        """
        <div class="login-form-card">
            <h2>Secure sign in</h2>
            <p class="subtitle">
                Enter your credentials to access the recruitment dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )

        submitted = st.form_submit_button(
            "Sign In",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not username.strip() or not password:
            st.warning("Please enter both username and password.")

        elif login_user(username, password):
            st.success("Login successful. Redirecting...")
            st.switch_page("app.py")

        else:
            st.error("Incorrect username or password. Please try again.")

    st.markdown(
        f"""
        <div class="login-security">
            🔒 Secure recruiter access. Credentials are verified locally
            against your organization's user database.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Use an account created by your system administrator.")

st.caption("AI Resume Analyzer v1.0 | Secure Recruitment Access")
