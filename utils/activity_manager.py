from database import get_connection


# ---------------------------------
# Add Candidate Activity
# ---------------------------------
def add_candidate_activity(
    candidate_id,
    activity_type,
    activity_title,
    activity_description="",
    performed_by=None,
    old_status=None,
    new_status=None,
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO candidate_activities (
                candidate_id,
                performed_by,
                activity_type,
                activity_title,
                activity_description,
                old_status,
                new_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                candidate_id,
                performed_by,
                activity_type,
                activity_title,
                activity_description or None,
                old_status,
                new_status,
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
# Get Candidate Activities
# ---------------------------------
def get_candidate_activities(candidate_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                ca.activity_id,
                ca.candidate_id,
                ca.activity_type,
                ca.activity_title,
                ca.activity_description,
                ca.old_status,
                ca.new_status,
                ca.created_at,
                u.full_name AS performed_by_name,
                u.role AS performed_by_role
            FROM candidate_activities ca
            LEFT JOIN users u
                ON ca.performed_by = u.user_id
            WHERE ca.candidate_id = %s
            ORDER BY ca.created_at DESC, ca.activity_id DESC
            """,
            (candidate_id,),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Get Recent Activities
# ---------------------------------
def get_recent_activities(limit=20):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                ca.activity_id,
                ca.candidate_id,
                r.name AS candidate_name,
                r.email AS candidate_email,
                ca.activity_type,
                ca.activity_title,
                ca.activity_description,
                ca.old_status,
                ca.new_status,
                ca.created_at,
                u.full_name AS performed_by_name
            FROM candidate_activities ca
            JOIN resumes r
                ON ca.candidate_id = r.id
            LEFT JOIN users u
                ON ca.performed_by = u.user_id
            ORDER BY ca.created_at DESC, ca.activity_id DESC
            LIMIT %s
            """,
            (limit,),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Delete Candidate Activity
# ---------------------------------
def delete_candidate_activity(activity_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM candidate_activities
            WHERE activity_id = %s
            """,
            (activity_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
