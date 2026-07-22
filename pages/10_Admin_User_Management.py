import pandas as pd
import streamlit as st
from utils.theme import apply_global_styles, page_header, render_kpi_row, section_header

from auth import (
    create_user,
    get_all_users,
    require_role,
    update_password,
    update_user_status,
)
from utils.sidebar import show_sidebar

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="User Management | AI Resume Analyzer",
    page_icon="👑",
    layout="wide",
)


# ---------------------------------
# Admin Access Only
# ---------------------------------
require_role("Admin")
apply_global_styles()
show_sidebar()

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
