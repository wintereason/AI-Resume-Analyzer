import os

import streamlit as st


def get_database_secret(name, default=""):
    try:
        if "database" in st.secrets:
            return st.secrets["database"].get(
                name,
                default,
            )
    except Exception:
        pass

    return os.getenv(
        f"DB_{name.upper()}",
        default,
    )


DB_CONFIG = {
    "host": get_database_secret(
        "host",
        "localhost",
    ),
    "user": get_database_secret(
        "user",
        "root",
    ),
    "password": get_database_secret(
        "password",
        "",
    ),
    "database": get_database_secret(
        "database",
        "ai_resume_analyzer",
    ),
    "port": int(
        get_database_secret(
            "port",
            "3306",
        )
    ),
}
