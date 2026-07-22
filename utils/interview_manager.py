from database import get_connection
from utils.activity_manager import add_candidate_activity


# ---------------------------------
# Create Interview
# ---------------------------------
def create_interview(
    candidate_id,
    scheduled_by,
    interview_date,
    interview_time,
    interview_mode,
    meeting_link="",
    location="",
    notes="",
):
    connection = get_connection()
    cursor = connection.cursor()

    interview_id = None

    try:
        cursor.execute(
            """
            INSERT INTO interviews (
                candidate_id,
                scheduled_by,
                interview_date,
                interview_time,
                interview_mode,
                meeting_link,
                location,
                notes,
                status
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, 'Scheduled'
            )
            """,
            (
                candidate_id,
                scheduled_by,
                interview_date,
                interview_time,
                interview_mode,
                meeting_link or None,
                location or None,
                notes or None,
            ),
        )

        interview_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE resumes
            SET status = 'Interview Scheduled'
            WHERE id = %s
            """,
            (candidate_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    try:
        add_candidate_activity(
            candidate_id=candidate_id,
            performed_by=scheduled_by,
            activity_type="interview_scheduled",
            activity_title="Interview scheduled",
            activity_description=(
                f"{interview_mode} interview scheduled for "
                f"{interview_date} at {interview_time}."
            ),
            old_status="Under Review",
            new_status="Interview Scheduled",
        )

    except Exception as activity_error:
        print(
            "Interview created, but activity could not "
            f"be recorded: {activity_error}"
        )

    return interview_id


# ---------------------------------
# Fetch All Interviews
# ---------------------------------
def get_all_interviews():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                i.interview_id,
                i.candidate_id,
                r.name AS candidate_name,
                r.email AS candidate_email,
                r.phone AS candidate_phone,
                r.ats_score,
                r.recommended_role,
                i.interview_date,
                i.interview_time,
                i.interview_mode,
                i.meeting_link,
                i.location,
                i.notes,
                i.status,
                i.created_at,
                u.full_name AS scheduled_by_name
            FROM interviews i
            JOIN resumes r
                ON i.candidate_id = r.id
            LEFT JOIN users u
                ON i.scheduled_by = u.user_id
            ORDER BY
                i.interview_date ASC,
                i.interview_time ASC
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Fetch Upcoming Interviews
# ---------------------------------
def get_upcoming_interviews():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                i.interview_id,
                i.candidate_id,
                r.name AS candidate_name,
                r.email AS candidate_email,
                r.phone AS candidate_phone,
                r.ats_score,
                r.recommended_role,
                i.interview_date,
                i.interview_time,
                i.interview_mode,
                i.meeting_link,
                i.location,
                i.notes,
                i.status,
                i.created_at,
                u.full_name AS scheduled_by_name
            FROM interviews i
            JOIN resumes r
                ON i.candidate_id = r.id
            LEFT JOIN users u
                ON i.scheduled_by = u.user_id
            WHERE
                i.status = 'Scheduled'
                AND (
                    i.interview_date > CURDATE()
                    OR (
                        i.interview_date = CURDATE()
                        AND i.interview_time >= CURTIME()
                    )
                )
            ORDER BY
                i.interview_date ASC,
                i.interview_time ASC
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Update Interview Status
# ---------------------------------
def update_interview_status(
    interview_id,
    candidate_id,
    new_status,
    performed_by=None,
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    candidate_status_map = {
        "Scheduled": "Interview Scheduled",
        "Completed": "Under Review",
        "Cancelled": "Under Review",
        "Rescheduled": "Interview Scheduled",
        "Candidate Absent": "Under Review",
    }

    old_interview_status = None
    old_candidate_status = None
    candidate_status = candidate_status_map.get(
        new_status,
        "Under Review",
    )

    try:
        cursor.execute(
            """
            SELECT status
            FROM interviews
            WHERE interview_id = %s
            """,
            (interview_id,),
        )

        interview_record = cursor.fetchone()

        if interview_record:
            old_interview_status = interview_record.get("status")

        cursor.execute(
            """
            SELECT status
            FROM resumes
            WHERE id = %s
            """,
            (candidate_id,),
        )

        candidate_record = cursor.fetchone()

        if candidate_record:
            old_candidate_status = candidate_record.get("status")

        cursor.execute(
            """
            UPDATE interviews
            SET status = %s
            WHERE interview_id = %s
            """,
            (
                new_status,
                interview_id,
            ),
        )

        cursor.execute(
            """
            UPDATE resumes
            SET status = %s
            WHERE id = %s
            """,
            (
                candidate_status,
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

    try:
        add_candidate_activity(
            candidate_id=candidate_id,
            performed_by=performed_by,
            activity_type="interview_status_updated",
            activity_title=(f"Interview marked as {new_status}"),
            activity_description=(
                f"Interview status changed from "
                f"{old_interview_status or 'Unknown'} "
                f"to {new_status}."
            ),
            old_status=old_candidate_status,
            new_status=candidate_status,
        )

    except Exception as activity_error:
        print(
            "Interview status updated, but activity "
            f"could not be recorded: {activity_error}"
        )

    return True


# ---------------------------------
# Reschedule Interview
# ---------------------------------
def reschedule_interview(
    interview_id,
    interview_date,
    interview_time,
    performed_by=None,
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    candidate_id = None
    old_date = None
    old_time = None

    try:
        cursor.execute(
            """
            SELECT
                candidate_id,
                interview_date,
                interview_time
            FROM interviews
            WHERE interview_id = %s
            """,
            (interview_id,),
        )

        interview_record = cursor.fetchone()

        if not interview_record:
            return False

        candidate_id = interview_record.get("candidate_id")
        old_date = interview_record.get("interview_date")
        old_time = interview_record.get("interview_time")

        cursor.execute(
            """
            UPDATE interviews
            SET
                interview_date = %s,
                interview_time = %s,
                status = 'Scheduled'
            WHERE interview_id = %s
            """,
            (
                interview_date,
                interview_time,
                interview_id,
            ),
        )

        cursor.execute(
            """
            UPDATE resumes
            SET status = 'Interview Scheduled'
            WHERE id = %s
            """,
            (candidate_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    try:
        add_candidate_activity(
            candidate_id=candidate_id,
            performed_by=performed_by,
            activity_type="interview_rescheduled",
            activity_title="Interview rescheduled",
            activity_description=(
                f"Interview changed from {old_date} at {old_time} "
                f"to {interview_date} at {interview_time}."
            ),
            old_status="Interview Scheduled",
            new_status="Interview Scheduled",
        )

    except Exception as activity_error:
        print(
            "Interview rescheduled, but activity "
            f"could not be recorded: {activity_error}"
        )

    return True


# ---------------------------------
# Delete Interview
# ---------------------------------
def delete_interview(
    interview_id,
    performed_by=None,
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    candidate_id = None
    interview_date = None
    interview_time = None

    try:
        cursor.execute(
            """
            SELECT
                candidate_id,
                interview_date,
                interview_time
            FROM interviews
            WHERE interview_id = %s
            """,
            (interview_id,),
        )

        interview_record = cursor.fetchone()

        if not interview_record:
            return False

        candidate_id = interview_record.get("candidate_id")
        interview_date = interview_record.get("interview_date")
        interview_time = interview_record.get("interview_time")

        cursor.execute(
            """
            DELETE FROM interviews
            WHERE interview_id = %s
            """,
            (interview_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    try:
        add_candidate_activity(
            candidate_id=candidate_id,
            performed_by=performed_by,
            activity_type="interview_deleted",
            activity_title="Interview record deleted",
            activity_description=(
                f"The interview scheduled for {interview_date} "
                f"at {interview_time} was deleted."
            ),
            old_status="Interview Scheduled",
            new_status=None,
        )

    except Exception as activity_error:
        print(
            "Interview deleted, but activity could "
            f"not be recorded: {activity_error}"
        )

    return True
