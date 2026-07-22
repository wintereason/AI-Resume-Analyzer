from database import get_connection


def get_resume_ranking():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        name,
        email,
        ats_score,
        skills
    FROM resumes
    ORDER BY ats_score DESC
    """

    cursor.execute(query)

    resumes = cursor.fetchall()

    cursor.close()
    conn.close()

    return resumes