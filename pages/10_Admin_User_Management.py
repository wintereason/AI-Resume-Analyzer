<<<<<<< HEAD
import pandas as pd
import streamlit as st
from utils.theme import apply_global_styles, page_header, render_kpi_row, section_header
=======
import html

import pandas as pd
import streamlit as st
>>>>>>> a1ff58d (Update UI and improve performance)

from auth import (
    create_user,
    get_all_users,
    require_role,
    update_password,
    update_user_status,
)
from utils.sidebar import show_sidebar
<<<<<<< HEAD
=======
from utils.ui_system import apply_ui_system
>>>>>>> a1ff58d (Update UI and improve performance)

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="User Management | AI Resume Analyzer",
    page_icon="👑",
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
        :root{--ink:#182033;--muted:#718096;--line:#E4EAF3;--canvas:#F3F6FB;--blue:#2466D1;--purple:#6846C7}
        html,body,[class*="css"]{font-family:'Inter',sans-serif}.stApp{background:var(--canvas);color:var(--ink)}header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1460px;padding:1rem 1.4rem 2.5rem}h1,h2,h3,h4,h5{color:var(--ink);letter-spacing:-.02em}p,label,.stCaption{color:var(--muted)}
        section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}section[data-testid="stSidebar"] .block-container{padding:1rem .85rem 1.25rem}section[data-testid="stSidebar"] div[data-testid="stSidebarNav"]{display:none}section[data-testid="stSidebar"] hr{border-color:#EDF0F5;margin:.7rem 0}
        section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]{min-height:40px;margin:2px 0;padding:8px 10px;border-radius:10px;color:#536078;font-size:.79rem;font-weight:600;border:1px solid transparent;transition:all .16s ease}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue);background:#F2F6FD;border-color:#E4EAF4;transform:translateX(2px)}section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]{color:#fff;background:linear-gradient(110deg,#1D58B8,#286CD6);box-shadow:0 7px 16px rgba(36,102,209,.18)}
        .sidebar-nav-label{margin:13px 4px 7px;color:#8A95A8;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.sidebar-account{display:flex;align-items:center;gap:10px;padding:11px;margin-bottom:9px;border:1px solid var(--line);border-radius:12px;background:#F8FAFD}.sidebar-account .name{color:var(--ink);font-size:.8rem;font-weight:800}.sidebar-account .meta{color:#8490A4;font-size:.66rem}.candidate-avatar{display:flex;align-items:center;justify-content:center;flex:0 0 auto;border-radius:50%;color:#fff;background:linear-gradient(135deg,var(--blue),var(--purple));font-weight:800}.status-badge{display:inline-block;padding:4px 9px;border:1px solid;border-radius:999px;font-size:.68rem;font-weight:800}.sidebar-status-row{display:grid;gap:6px;margin:8px 3px}.sidebar-status-item{display:flex;align-items:center;gap:7px;color:#7C889C;font-size:.67rem}.sidebar-dot{width:7px;height:7px;border-radius:50%}
        .admin-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:21px 23px;margin-bottom:16px;border-radius:18px;color:#fff;background:linear-gradient(110deg,#392E83 0%,#5147C6 50%,#2466D1 100%);box-shadow:0 12px 28px rgba(55,47,132,.18)}.admin-hero .eyebrow{color:rgba(255,255,255,.7);font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.admin-hero h1{margin:4px 0;color:#fff;font-size:1.55rem;font-weight:800}.admin-hero p{margin:0;max-width:800px;color:rgba(255,255,255,.76);font-size:.8rem}.admin-icon{width:52px;height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 52px;border-radius:15px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:1.4rem}
        .admin-metric{min-height:122px;padding:17px 18px;border-radius:15px;color:#fff;position:relative;overflow:hidden;box-shadow:0 9px 21px rgba(39,55,93,.12)}.admin-metric:after{content:"";position:absolute;width:90px;height:90px;right:-30px;top:-45px;border-radius:50%;background:rgba(255,255,255,.16)}.metric-icon{width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.17)}.metric-label{margin-top:10px;color:rgba(255,255,255,.8);font-size:.68rem;font-weight:700}.metric-value{margin-top:3px;font-size:1.48rem;font-weight:800;line-height:1}.metric-note{margin-top:7px;color:rgba(255,255,255,.7);font-size:.65rem}
        div[data-testid="stForm"]{padding:20px;background:#fff;border:1px solid var(--line);border-radius:15px;box-shadow:0 7px 20px rgba(35,52,84,.055)}div[data-testid="stSelectbox"]>div>div,div[data-testid="stTextInput"] input{background:#fff;border-color:#DDE5F0;border-radius:10px}div[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 7px 20px rgba(35,52,84,.055);overflow:hidden}div[data-testid="stDataFrame"] [role="columnheader"]{background:#F7F9FC;color:#59667C;font-weight:700}
        div[data-testid="stMetric"]{padding:14px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 17px rgba(35,52,84,.05)}div[data-testid="stMetricValue"]{color:var(--ink);font-weight:800}div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button,div[data-testid="stDownloadButton"] button{min-height:42px;border-radius:10px;border:1px solid #D8E1EF;font-weight:700}div[data-testid="stButton"] button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"]{color:#fff;background:var(--blue);border-color:var(--blue)}div[data-testid="stAlert"]{border-radius:12px;border-width:1px}hr{border-color:#E7EBF2;margin:1.3rem 0}h3{font-size:1rem!important;font-weight:800!important}@media(max-width:850px){.admin-icon{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title,description="",icon="",eyebrow="Administration"):
    st.markdown(f'<div class="admin-hero"><div><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></div><div class="admin-icon">{escape(icon or "♛")}</div></div>',unsafe_allow_html=True)


def metric_card(label,value,icon,start,end,note):
    st.markdown(f'<div class="admin-metric" style="background:linear-gradient(135deg,{start},{end})"><div class="metric-icon">{escape(icon)}</div><div class="metric-label">{escape(label)}</div><div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>',unsafe_allow_html=True)


>>>>>>> a1ff58d (Update UI and improve performance)
# ---------------------------------
# Admin Access Only
# ---------------------------------
require_role("Admin")
apply_global_styles()
show_sidebar()
<<<<<<< HEAD
=======
apply_ui_system()
>>>>>>> a1ff58d (Update UI and improve performance)

page_header(
    title="Admin User Management",
    description=(
        "Create recruiter accounts, manage access, reset passwords, "
        "and monitor system users."
    ),
    icon="👑",
)


# ---------------------------------
# Create User Account
# ---------------------------------
st.subheader("➕ Create New User")


with st.form("create_user_form"):

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        full_name = st.text_input(
            "Full Name",
            placeholder="Example: Rahul Sharma",
        )

        username = st.text_input(
            "Username",
            placeholder="Example: rahul.hr",
        )

    with form_col2:
        role = st.selectbox(
            "User Role",
            options=[
                "Recruiter",
                "Admin",
            ],
        )

        password = st.text_input(
            "Temporary Password",
            type="password",
            placeholder="Minimum 8 characters",
        )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
    )

    create_submitted = st.form_submit_button(
        "✅ Create User Account",
        type="primary",
        width="stretch",
    )


if create_submitted:

    if not full_name.strip():
        st.warning("Please enter the user's full name.")

    elif not username.strip():
        st.warning("Please enter a username.")

    elif not password:
        st.warning("Please enter a password.")

    elif password != confirm_password:
        st.error("Passwords do not match.")

    else:
        try:
            user_id = create_user(
                full_name=full_name,
                username=username,
                password=password,
                role=role,
            )

            st.success(f"✅ User account created successfully. " f"User ID: {user_id}")

            st.rerun()

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(f"Unable to create user account: {error}")


st.divider()


# ---------------------------------
# Load Users
# ---------------------------------
st.subheader("👥 Registered Users")


try:
    users = get_all_users()

except Exception as error:
    st.error(f"Unable to load users: {error}")
    st.stop()


if not users:
    st.info("No user accounts are available.")
    st.stop()


users_df = pd.DataFrame(users)


# ---------------------------------
# User Statistics
# ---------------------------------
total_users = len(users_df)

admin_count = len(users_df[users_df["role"].astype(str).str.lower() == "admin"])

recruiter_count = len(users_df[users_df["role"].astype(str).str.lower() == "recruiter"])

active_count = len(users_df[users_df["is_active"].astype(bool)])


metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)


with metric_col1:
<<<<<<< HEAD
    st.metric(
        "👥 Total Users",
        total_users,
    )


with metric_col2:
    st.metric(
        "👑 Admins",
        admin_count,
    )


with metric_col3:
    st.metric(
        "👨‍💼 Recruiters",
        recruiter_count,
    )


with metric_col4:
    st.metric(
        "🟢 Active Accounts",
        active_count,
    )
=======
    metric_card("Total Users",total_users,"♙","#5147C6","#6655D5","All system accounts")


with metric_col2:
    metric_card("Admins",admin_count,"♛","#6846C7","#8359D0","Administrative access")


with metric_col3:
    metric_card("Recruiters",recruiter_count,"◇","#0879B9","#1598D0","Recruitment operators")


with metric_col4:
    metric_card("Active Accounts",active_count,"✓","#13A875","#1BC58A","Enabled user access")
>>>>>>> a1ff58d (Update UI and improve performance)


st.divider()


# ---------------------------------
# Search and Filter
# ---------------------------------
st.subheader("🔍 Search and Filter Users")


filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])


with filter_col1:
    search_text = st.text_input(
        "Search users",
        placeholder="Search by name or username",
    )


with filter_col2:
    selected_role = st.selectbox(
        "Filter by Role",
        options=[
            "All",
            "Admin",
            "Recruiter",
        ],
    )


with filter_col3:
    selected_account_status = st.selectbox(
        "Account Status",
        options=[
            "All",
            "Active",
            "Disabled",
        ],
    )


filtered_users_df = users_df.copy()


if search_text:
    search_value = search_text.strip()

    filtered_users_df = filtered_users_df[
        filtered_users_df["full_name"].str.contains(
            search_value,
            case=False,
            na=False,
        )
        | filtered_users_df["username"].str.contains(
            search_value,
            case=False,
            na=False,
        )
    ]


if selected_role != "All":
    filtered_users_df = filtered_users_df[filtered_users_df["role"] == selected_role]


if selected_account_status == "Active":
    filtered_users_df = filtered_users_df[filtered_users_df["is_active"].astype(bool)]

elif selected_account_status == "Disabled":
    filtered_users_df = filtered_users_df[~filtered_users_df["is_active"].astype(bool)]


st.caption(f"Showing {len(filtered_users_df)} of " f"{len(users_df)} users")


# ---------------------------------
# User Table
# ---------------------------------
display_users_df = filtered_users_df.copy()

display_users_df["Account Status"] = display_users_df["is_active"].apply(
    lambda value: "Active" if value else "Disabled"
)

display_users_df = display_users_df.rename(
    columns={
        "user_id": "User ID",
        "full_name": "Full Name",
        "username": "Username",
        "role": "Role",
        "created_at": "Created At",
    }
)

display_users_df = display_users_df[
    [
        "User ID",
        "Full Name",
        "Username",
        "Role",
        "Account Status",
        "Created At",
    ]
]


st.dataframe(
    display_users_df,
    width="stretch",
    hide_index=True,
)


st.divider()


# ---------------------------------
# Select User to Manage
# ---------------------------------
st.subheader("⚙️ Manage User Account")


user_options = {
    (
        f"{user['full_name']} — "
        f"{user['username']} — "
        f"{user['role']} — ID {user['user_id']}"
    ): user
    for user in users
}


selected_user_label = st.selectbox(
    "Select a user",
    options=list(user_options.keys()),
)


selected_user = user_options[selected_user_label]


selected_user_id = selected_user["user_id"]
selected_username = selected_user["username"]
selected_full_name = selected_user["full_name"]
selected_user_role = selected_user["role"]
selected_is_active = bool(selected_user["is_active"])


profile_col1, profile_col2, profile_col3 = st.columns(3)


with profile_col1:
    st.metric(
        "User",
        selected_full_name,
    )


with profile_col2:
    st.metric(
        "Role",
        selected_user_role,
    )


with profile_col3:
    st.metric(
        "Account Status",
        "Active" if selected_is_active else "Disabled",
    )


st.write(f"**Username:** {selected_username}")


st.divider()


# ---------------------------------
# Activate / Disable User
# ---------------------------------
st.subheader("🟢 Account Access")


if selected_user_id == st.session_state.get("user_id"):
    st.info("You cannot disable the account currently being used.")

else:
    new_active_status = st.toggle(
        "Account Active",
        value=selected_is_active,
        key=f"active_status_{selected_user_id}",
    )

    if st.button(
        "💾 Update Account Status",
        width="stretch",
        type="primary",
    ):
        try:
            updated = update_user_status(
                selected_user_id,
                new_active_status,
            )

            if updated:
                status_text = "activated" if new_active_status else "disabled"

                st.success(f"Account {status_text} successfully.")

                st.rerun()

            else:
                st.warning("The user account could not be updated.")

        except Exception as error:
            st.error(f"Unable to update account status: {error}")


st.divider()


# ---------------------------------
# Reset Password
# ---------------------------------
st.subheader("🔑 Reset User Password")


with st.form(f"password_reset_form_{selected_user_id}"):

    new_password = st.text_input(
        "New Password",
        type="password",
        placeholder="Minimum 8 characters",
    )

    confirm_new_password = st.text_input(
        "Confirm New Password",
        type="password",
    )

    reset_submitted = st.form_submit_button(
        "🔐 Reset Password",
        width="stretch",
    )


if reset_submitted:

    if len(new_password) < 8:
        st.warning("Password must contain at least 8 characters.")

    elif new_password != confirm_new_password:
        st.error("Passwords do not match.")

    else:
        try:
            updated = update_password(
                selected_user_id,
                new_password,
            )

            if updated:
                st.success(f"Password reset successfully for " f"{selected_username}.")

            else:
                st.warning("The selected user could not be found.")

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(f"Unable to reset password: {error}")


st.divider()


# ---------------------------------
# Export Users
# ---------------------------------
st.subheader("📥 Export User List")


export_df = display_users_df.copy()

csv_data = export_df.to_csv(index=False).encode("utf-8")


st.download_button(
    label="⬇️ Download User List",
    data=csv_data,
    file_name="system_users.csv",
    mime="text/csv",
    width="stretch",
)


st.caption("AI Resume Analyzer v1.0 | Admin User Management")
