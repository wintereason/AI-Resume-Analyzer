from database import get_connection


# ---------------------------------
# Fetch All Resumes
# ---------------------------------
def get_all_resumes():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                education,
                skills,
                projects,
                ats_score,
                recommended_role,
                status
            FROM resumes
            ORDER BY id DESC
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Fetch One Resume
# ---------------------------------
def get_resume_by_id(resume_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                education,
                skills,
                projects,
                ats_score,
                recommended_role,
                status
            FROM resumes
            WHERE id = %s
            """,
            (resume_id,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Delete Resume
# ---------------------------------
def delete_resume(resume_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM resumes
            WHERE id = %s
            """,
            (resume_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
