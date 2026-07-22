import streamlit as st

from auth import initialize_auth, logout_user
from database import get_connection
from utils.theme import COLORS, escape_html, get_initials


APP_VERSION = "1.0.0"

NAV_ITEMS = [
    ("Dashboard", "pages/1_Dashboard.py", "📊"),
    ("Upload Resume", "pages/2_Upload_Resume.py", "📤"),
    ("Saved Resumes", "pages/3_Saved_Resumes.py", "📁"),
    ("Analytics", "pages/4_Analytics.py", "📈"),
    ("Job Recommendation", "pages/6_Job_Recommendations.py", "💼"),
    ("Skill Gap", "pages/7_Skill_Gap_Analysis.py", "🎯"),
    ("Recruiter Dashboard", "pages/7_Recruiter_Dashboard.py", "🧑‍💼"),
    ("Job Matching", "pages/8_Job_Matching.py", "🔗"),
    ("Candidate Profile", "pages/11_Candidate_Profile.py", "👤"),
    ("Interview Scheduler", "pages/12_Interview_Scheduler.py", "📅"),
]


def _check_database_status():
    """Return True if the database connection is reachable."""
    try:
        connection = get_connection()
        connection.close()
        return True

    except Exception:
        return False


def show_sidebar():
    """Render a compact professional sidebar."""
    initialize_auth()

    st.sidebar.markdown(
        f"""
        <div style="padding:4px 0 16px 0;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div style="width:36px;height:36px;border-radius:10px;
                            display:flex;align-items:center;justify-content:center;
                            background:rgba(79,124,255,0.16);
                            border:1px solid {COLORS["border_strong"]};
                            font-size:1.1rem;">🤖</div>
                <div>
                    <div style="font-size:1rem;font-weight:800;color:{COLORS["text"]};
                                line-height:1.2;">
                        AI Resume Analyzer
                    </div>
                    <div style="color:{COLORS["muted"]};font-size:0.74rem;">
                        Smart Recruitment Platform
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    logged_in = st.session_state.get("logged_in", False)

    if logged_in:
        user_name = st.session_state.get("user_name") or "User"
        user_role = st.session_state.get("user_role") or "Recruiter"
        initials = escape_html(get_initials(user_name))
        role_color, _ = (
            ("#8B5CF6", "Admin")
            if user_role == "Admin"
<<<<<<< HEAD
            else ("#4F7CFF", user_role)
=======
            else ("#2563C9", user_role)
>>>>>>> a1ff58d (Update UI and improve performance)
        )

        st.sidebar.markdown(
            f"""
            <div class="sidebar-account">
                <div class="candidate-avatar"
                     style="width:40px;height:40px;font-size:0.78rem;">
                    {initials}
                </div>
                <div style="flex:1;min-width:0;">
                    <div class="name">{escape_html(user_name)}</div>
                    <div class="meta">Signed in securely</div>
                    <span class="status-badge"
                          style="margin-top:6px;display:inline-block;
                                 color:{role_color};background:{role_color}22;
                                 border-color:{role_color}44;">
                        {escape_html(user_role)}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            '<div class="sidebar-nav-label">Navigation</div>',
            unsafe_allow_html=True,
        )

        for label, page_path, icon in NAV_ITEMS:
            st.sidebar.page_link(page_path, label=label, icon=icon)

        if user_role == "Admin":
            st.sidebar.page_link(
                "pages/10_Admin_User_Management.py",
                label="User Management",
                icon="⚙️",
            )

        st.sidebar.divider()

        if st.sidebar.button(
            "Logout",
            width="stretch",
            key="sidebar_logout",
            type="primary",
        ):
            logout_user()
            st.switch_page("pages/0_Login.py")

    else:
        st.sidebar.markdown(
            f"""
            <div class="info-card" style="margin-bottom:12px;">
                <h4>Sign in required</h4>
                <p>Access candidate records, analytics, and recruitment tools.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.sidebar.button(
            "Go to Login",
            width="stretch",
            key="sidebar_login",
            type="primary",
        ):
            st.switch_page("pages/0_Login.py")

    st.sidebar.divider()

    db_online = _check_database_status()
    db_color = COLORS["green"] if db_online else COLORS["red"]
    db_text = "Connected" if db_online else "Offline"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-status-row">
            <div class="sidebar-status-item">
                <span class="sidebar-dot" style="background:{COLORS["green"]};"></span>
                Secure session active
            </div>
            <div class="sidebar-status-item">
                <span class="sidebar-dot" style="background:{db_color};"></span>
                Database {db_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.caption(f"v{APP_VERSION}")
