from database import get_connection
from utils.activity_manager import add_candidate_activity

ALLOWED_STATUSES = [
    "Review Required",
    "Under Review",
    "Shortlisted",
    "Interview Scheduled",
    "Selected",
    "Rejected",
]


def get_candidate_status(candidate_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT status
            FROM resumes
            WHERE id = %s
            """,
            (candidate_id,),
        )

        record = cursor.fetchone()

        if not record:
            return None

        return record.get("status")

    finally:
        cursor.close()
        connection.close()


def update_candidate_status(
    candidate_id,
    new_status,
    performed_by=None,
    note="",
):
    """
    Update candidate recruitment status and create
    an activity timeline record.
    """

    if new_status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid candidate status: {new_status}")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    old_status = None

    try:
        cursor.execute(
            """
            SELECT status
            FROM resumes
            WHERE id = %s
            """,
            (candidate_id,),
        )

        candidate = cursor.fetchone()

        if not candidate:
            return False

        old_status = candidate.get("status") or "Under Review"

        if old_status == new_status:
            return False

        cursor.execute(
            """
            UPDATE resumes
            SET status = %s
            WHERE id = %s
            """,
            (
                new_status,
                candidate_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    activity_type_map = {
        "Review Required": "status_updated",
        "Under Review": "status_updated",
        "Shortlisted": "candidate_shortlisted",
        "Interview Scheduled": "interview_scheduled",
        "Selected": "candidate_selected",
        "Rejected": "candidate_rejected",
    }

    activity_title_map = {
        "Review Required": "Candidate requires additional review",
        "Under Review": "Candidate moved to review",
        "Shortlisted": "Candidate shortlisted",
        "Interview Scheduled": "Candidate moved to interview stage",
        "Selected": "Candidate selected",
        "Rejected": "Candidate rejected",
    }

    try:
        add_candidate_activity(
            candidate_id=candidate_id,
            performed_by=performed_by,
            activity_type=activity_type_map[new_status],
            activity_title=activity_title_map[new_status],
            activity_description=(
                note.strip()
                if note and note.strip()
                else (
                    f"Candidate status changed from " f"{old_status} to {new_status}."
                )
            ),
            old_status=old_status,
            new_status=new_status,
        )

    except Exception as activity_error:
        print(
            "Candidate status updated, but activity "
            f"could not be recorded: {activity_error}"
        )

    return True
