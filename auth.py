import hashlib
import hmac
import os

import streamlit as st

from database import get_connection


# ---------------------------------
# Password Configuration
# ---------------------------------
PBKDF2_ITERATIONS = 200_000


# ---------------------------------
# Initialize Login Session
# ---------------------------------
def initialize_auth():
    default_values = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "user_role": None,
        "user_name": None,
    }

    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# ---------------------------------
# Password Hashing
# ---------------------------------
def generate_salt():
    """
    Generate a random salt for password hashing.
    """

    return os.urandom(16).hex()


def hash_password(password, salt):
    """
    Hash a password using PBKDF2-HMAC-SHA256.
    """

    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty.")

    if not isinstance(salt, str) or not salt:
        raise ValueError("Password salt cannot be empty.")

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PBKDF2_ITERATIONS,
    )

    return password_hash.hex()


def verify_password(password, salt, saved_password_hash):
    """
    Safely verify the entered password.
    """

    try:
        entered_password_hash = hash_password(
            password,
            salt,
        )

        return hmac.compare_digest(
            entered_password_hash,
            saved_password_hash,
        )

    except (TypeError, ValueError):
        return False


# ---------------------------------
# Fetch User by Username
# ---------------------------------
def get_user_by_username(username):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                username,
                password_hash,
                password_salt,
                role,
                is_active,
                created_at
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username.strip().lower(),),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Check Username
# ---------------------------------
def username_exists(username):
    return get_user_by_username(username) is not None


# ---------------------------------
# Create User
# ---------------------------------
def create_user(
    full_name,
    username,
    password,
    role="Recruiter",
):
    full_name = str(full_name or "").strip()
    username = str(username or "").strip().lower()
    password = str(password or "")
    role = str(role or "Recruiter").strip()

    if not full_name:
        raise ValueError("Full name is required.")

    if len(username) < 3:
        raise ValueError(
            "Username must contain at least 3 characters."
        )

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    allowed_roles = {
        "Admin",
        "Recruiter",
    }

    if role not in allowed_roles:
        raise ValueError("Invalid user role.")

    if username_exists(username):
        raise ValueError(
            "This username is already registered."
        )

    salt = generate_salt()

    password_hash = hash_password(
        password,
        salt,
    )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                username,
                password_hash,
                password_salt,
                role,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s, TRUE)
            """,
            (
                full_name,
                username,
                password_hash,
                salt,
                role,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Login User
# ---------------------------------
def login_user(username, password):
    initialize_auth()

    username = str(username or "").strip().lower()
    password = str(password or "")

    if not username or not password:
        return False

    user = get_user_by_username(username)

    if not user:
        return False

    if not user.get("is_active"):
        return False

    password_is_correct = verify_password(
        password,
        user.get("password_salt", ""),
        user.get("password_hash", ""),
    )

    if not password_is_correct:
        return False

    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["user_id"]
    st.session_state["username"] = user["username"]
    st.session_state["user_role"] = user["role"]
    st.session_state["user_name"] = user["full_name"]

    return True


# ---------------------------------
# Logout User
# ---------------------------------
def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None


# ---------------------------------
# Require Login
# ---------------------------------
def require_login():
    initialize_auth()

    if not st.session_state["logged_in"]:
        st.warning(
            "🔐 Please log in to access this page."
        )

        if st.button(
            "Go to Login",
            width="stretch",
        ):
            st.switch_page("pages/0_Login.py")

        st.stop()


# ---------------------------------
# Require Specific Role
# ---------------------------------
def require_role(allowed_roles):
    require_login()

    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    if st.session_state["user_role"] not in allowed_roles:
        st.error(
            "⛔ You do not have permission to access this page."
        )

        st.info(
            f"Required role: {', '.join(allowed_roles)}"
        )

        st.stop()


# ---------------------------------
# Update User Password
# ---------------------------------
def update_password(user_id, new_password):
    if len(new_password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    salt = generate_salt()

    password_hash = hash_password(
        new_password,
        salt,
    )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET
                password_hash = %s,
                password_salt = %s
            WHERE user_id = %s
            """,
            (
                password_hash,
                salt,
                user_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Activate or Disable User
# ---------------------------------
def update_user_status(user_id, is_active):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET is_active = %s
            WHERE user_id = %s
            """,
            (
                bool(is_active),
                user_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Fetch All Users
# ---------------------------------
def get_all_users():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                username,
                role,
                is_active,
                created_at
            FROM users
            ORDER BY user_id DESC
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Show Logged-in User
# ---------------------------------
def show_user_info():
    initialize_auth()

    if st.session_state["logged_in"]:
        st.sidebar.divider()

        st.sidebar.markdown("### 👤 Logged-in User")

        st.sidebar.write(
            f"**Name:** {st.session_state['user_name']}"
        )

        st.sidebar.write(
            f"**Username:** "
            f"{st.session_state['username']}"
        )

        st.sidebar.write(
            f"**Role:** {st.session_state['user_role']}"
        )

        if st.sidebar.button(
            "🚪 Logout",
            width="stretch",
        ):
            logout_user()
            st.switch_page("pages/0_Login.py")