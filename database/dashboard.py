from database.db import get_connection
from ai_resume_analyzer.database.dashboard import (
    get_total_resumes,
    get_average_ats,
    get_total_skills,
    get_recent_candidates
)


# ----------------------------------
# Total Resumes
# ----------------------------------
def get_total_resumes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM resumes"
    )

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


# ----------------------------------
# Average ATS Score
# ----------------------------------
def get_average_ats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT AVG(ats_score) FROM resumes"
    )

    avg = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return round(avg if avg else 0, 2)


# ----------------------------------
# Total Skills
# ----------------------------------
def get_total_skills():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT skills FROM resumes"
    )

    skills = cursor.fetchall()

    total = 0

    for row in skills:

        if row[0]:

            total += len(
                row[0].split(",")
            )

    cursor.close()
    conn.close()

    return total


# ----------------------------------
# Recent Candidates
# ----------------------------------
def get_recent_candidates(limit=5):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        f"""
        SELECT
            name,
            email,
            ats_score,
            recommended_role,
            status
        FROM resumes
        ORDER BY id DESC
        LIMIT {limit}
        """
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


# ----------------------------------
# Total Job Roles
# ----------------------------------
def get_total_job_roles():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM job_roles")
        result = cursor.fetchone()

        return result[0] if result else 0

    finally:
        cursor.close()
        conn.close()


# ----------------------------------
# ATS Score Distribution
# ----------------------------------
def get_ats_distribution():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

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
        conn.close()


    # ----------------------------------
    # Candidate Status Distribution
    # ----------------------------------
    def get_status_distribution():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    
        try:
            cursor.execute("""
                SELECT
                    COALESCE(status, 'Not Assigned') AS candidate_status,
                    COUNT(*) AS candidate_count
                FROM resumes
                GROUP BY candidate_status
                ORDER BY candidate_count DESC
                """)
    
            return cursor.fetchall()
    
        finally:
            cursor.close()
            conn.close()
