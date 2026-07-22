from database import get_connection


def get_total_resumes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM resumes")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


def get_total_job_roles():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM job_roles")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


def get_total_skills():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM skills")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total