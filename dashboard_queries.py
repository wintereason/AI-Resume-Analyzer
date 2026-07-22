from database import get_connection


def get_total_resumes():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM resumes")
        result = cursor.fetchone()

        return result[0] if result else 0

    finally:
        cursor.close()
        connection.close()


def get_average_ats():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT AVG(ats_score) FROM resumes")
        result = cursor.fetchone()

        average_score = result[0] if result else 0

        return round(float(average_score or 0), 2)

    finally:
        cursor.close()
        connection.close()


def get_total_skills():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT skills FROM resumes")
        rows = cursor.fetchall()

        unique_skills = set()

        for row in rows:
            skills_text = row[0]

            if skills_text:
                for skill in skills_text.split(","):
                    cleaned_skill = skill.strip().lower()

                    if cleaned_skill:
                        unique_skills.add(cleaned_skill)

        return len(unique_skills)

    finally:
        cursor.close()
        connection.close()


def get_total_job_roles():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM job_roles")
        result = cursor.fetchone()

        return result[0] if result else 0

    finally:
        cursor.close()
        connection.close()


def get_ats_distribution():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                CASE
                    WHEN ats_score < 50 THEN 'Below 50'
                    WHEN ats_score BETWEEN 50 AND 60 THEN '50-60'
                    WHEN ats_score BETWEEN 61 AND 70 THEN '61-70'
                    WHEN ats_score BETWEEN 71 AND 80 THEN '71-80'
                    WHEN ats_score BETWEEN 81 AND 90 THEN '81-90'
                    ELSE 'Above 90'
                END AS score_range,
                COUNT(*) AS resume_count
            FROM resumes
            WHERE ats_score IS NOT NULL
            GROUP BY score_range
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_status_distribution():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                COALESCE(
                    NULLIF(status, ''),
                    'Not Assigned'
                ) AS candidate_status,
                COUNT(*) AS candidate_count
            FROM resumes
            GROUP BY candidate_status
            ORDER BY candidate_count DESC
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_recent_candidates(limit=5):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                name,
                email,
                ats_score,
                recommended_role,
                status
            FROM resumes
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()
