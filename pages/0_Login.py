<<<<<<< HEAD
import streamlit as st
=======
import html

import streamlit as st
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

from auth import (
    initialize_auth,
    login_user,
    logout_user,
)
<<<<<<< HEAD
from utils.theme import apply_global_styles, escape_html
=======
>>>>>>> a1ff58d (Update UI and improve performance)

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
<<<<<<< HEAD
apply_global_styles()
=======


def escape_html(value):
    return html.escape(str(value or ""), quote=True)


def apply_global_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--blue:#2466D1;--purple:#6846C7}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:#F3F6FB;color:var(--ink)}
        header[data-testid="stHeader"]{background:transparent}section[data-testid="stSidebar"]{display:none}.block-container{max-width:1180px;padding:3.2rem 1.5rem 2rem}h1,h2,h3,h4{letter-spacing:-.025em}
        .login-brand-panel{min-height:610px;padding:45px 42px;border-radius:24px;color:#fff;background:radial-gradient(circle at 85% 8%,rgba(255,255,255,.16),transparent 32%),linear-gradient(145deg,#123F8C 0%,#2466D1 55%,#6846C7 100%);box-shadow:0 22px 55px rgba(39,68,132,.22);position:relative;overflow:hidden}
        .login-brand-panel:after{content:"";position:absolute;width:260px;height:260px;border-radius:50%;right:-120px;bottom:-130px;border:42px solid rgba(255,255,255,.06)}
        .login-brand-logo{width:54px;height:54px;display:flex;align-items:center;justify-content:center;border-radius:16px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.45rem;margin-bottom:28px}
        .login-brand-panel h1{margin:0 0 10px;color:#fff;font-size:2rem;font-weight:800}.login-brand-panel .tagline{max-width:560px;margin:0 0 34px;color:rgba(255,255,255,.74);font-size:.88rem;line-height:1.65}
        .login-feature{display:flex;align-items:flex-start;gap:13px;padding:13px 0;position:relative;z-index:2}.login-feature-icon{width:38px;height:38px;display:flex;align-items:center;justify-content:center;flex:0 0 38px;border-radius:11px;background:rgba(255,255,255,.14)}
        .login-feature strong{display:block;color:#fff;font-size:.82rem}.login-feature span{display:block;margin-top:3px;color:rgba(255,255,255,.68);font-size:.73rem;line-height:1.45}
        .login-form-card{margin-top:55px;padding:0 4px 18px}.login-form-card h2{margin:0 0 7px;color:var(--ink);font-size:1.55rem;font-weight:800}.login-form-card .subtitle{margin:0;color:var(--muted);font-size:.8rem}
        div[data-testid="stForm"]{padding:25px 24px;background:#fff;border:1px solid var(--line);border-radius:17px;box-shadow:0 12px 30px rgba(35,52,84,.08)}div[data-testid="stTextInput"] input{min-height:46px;background:#F8FAFD;border-color:#DDE5F0;border-radius:10px}div[data-testid="stTextInput"] input:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(36,102,209,.1)}
        div[data-testid="stFormSubmitButton"] button,div[data-testid="stButton"] button{min-height:44px;border-radius:10px;font-weight:800}div[data-testid="stFormSubmitButton"] button[kind="primary"],div[data-testid="stButton"] button[kind="primary"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);border-color:#2466D1;box-shadow:0 8px 18px rgba(36,102,209,.18)}
        .login-security{margin-top:14px;padding:12px 14px;border:1px solid #DCE8FA;border-radius:11px;background:#F3F7FE;color:#587093;font-size:.7rem;line-height:1.5}.saas-panel-card{padding:15px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}.saas-panel-card h4{margin:0;color:var(--ink)}.saas-panel-card .meta{margin:5px 0 0;color:var(--muted);font-size:.76rem;line-height:1.55}
        div[data-testid="stAlert"]{border-radius:11px}.stCaption{color:#8B96A8}@media(max-width:800px){.block-container{padding-top:1.2rem}.login-brand-panel{min-height:auto;padding:30px 25px}.login-form-card{margin-top:10px}}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_global_styles()
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)


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
