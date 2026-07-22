import os
import smtplib
from email.message import EmailMessage

import streamlit as st

from utils.activity_manager import add_candidate_activity


def get_email_config():
    """
    Read SMTP credentials from Streamlit secrets first,
    then fall back to environment variables.
    """

    try:
        email_config = st.secrets.get("email", {})
    except Exception:
        email_config = {}

    return {
        "smtp_host": email_config.get(
            "smtp_host",
            os.getenv("SMTP_HOST", "smtp.gmail.com"),
        ),
        "smtp_port": int(
            email_config.get(
                "smtp_port",
                os.getenv("SMTP_PORT", "587"),
            )
        ),
        "sender_email": email_config.get(
            "sender_email",
            os.getenv("SENDER_EMAIL", ""),
        ),
        "sender_password": email_config.get(
            "sender_password",
            os.getenv("SENDER_PASSWORD", ""),
        ),
        "sender_name": email_config.get(
            "sender_name",
            os.getenv(
                "SENDER_NAME",
                "AI Resume Analyzer Recruitment Team",
            ),
        ),
    }


def validate_email_config(config):
    if not config["sender_email"]:
        raise ValueError("Sender email is not configured.")

    if not config["sender_password"]:
        raise ValueError("Sender email password is not configured.")


def send_candidate_email(
    candidate_id,
    recipient_email,
    subject,
    body,
    performed_by=None,
    email_type="general",
):
    """
    Send an email and record it in the candidate timeline.
    """

    recipient_email = str(recipient_email or "").strip()

    subject = str(subject or "").strip()
    body = str(body or "").strip()

    if not recipient_email or "@" not in recipient_email:
        raise ValueError("A valid candidate email address is required.")

    if not subject:
        raise ValueError("Email subject cannot be empty.")

    if not body:
        raise ValueError("Email body cannot be empty.")

    config = get_email_config()
    validate_email_config(config)

    message = EmailMessage()

    message["From"] = f"{config['sender_name']} " f"<{config['sender_email']}>"

    message["To"] = recipient_email
    message["Subject"] = subject

    message.set_content(body)

    try:
        with smtplib.SMTP(
            config["smtp_host"],
            config["smtp_port"],
            timeout=30,
        ) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                config["sender_email"],
                config["sender_password"],
            )

            server.send_message(message)

    except smtplib.SMTPAuthenticationError as error:
        raise RuntimeError(
            "Email authentication failed. " "Check the sender email and app password."
        ) from error

    except smtplib.SMTPException as error:
        raise RuntimeError(f"SMTP email error: {error}") from error

    except OSError as error:
        raise RuntimeError(f"Unable to connect to the email server: {error}") from error

    activity_title_map = {
        "interview": "Interview invitation email sent",
        "selection": "Selection email sent",
        "rejection": "Rejection email sent",
        "offer": "Offer email sent",
    }

    activity_title = activity_title_map.get(
        email_type,
        "Candidate email sent",
    )

    try:
        add_candidate_activity(
            candidate_id=candidate_id,
            performed_by=performed_by,
            activity_type="email_sent",
            activity_title=activity_title,
            activity_description=(f'Email "{subject}" sent to ' f"{recipient_email}."),
        )

    except Exception as activity_error:
        print("Email sent, but activity could not " f"be recorded: {activity_error}")

    return True
