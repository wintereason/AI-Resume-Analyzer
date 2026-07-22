from database import get_connection



def get_all_skills():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill_name
        FROM skills
    """)

    skills = cursor.fetchall()

    cursor.close()
    conn.close()

    return [skill[0] for skill in skills]