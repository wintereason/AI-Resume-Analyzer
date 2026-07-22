from database import get_connection


def normalize_skills(value):
    if value is None:
        return []

    if isinstance(value, str):
        return [skill.strip() for skill in value.split(",") if skill.strip()]

    return [str(skill).strip() for skill in value if str(skill).strip()]


def get_skill_gap(job_title, resume_skills):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT s.skill_name
            FROM skills s
            JOIN job_role_skills jrs
                ON s.skill_id = jrs.skill_id
            JOIN job_roles jr
                ON jrs.job_role_id = jr.job_role_id
            WHERE jr.job_title = %s
            """,
            (job_title,),
        )

        records = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    required_skills = [record["skill_name"] for record in records]

    clean_resume_skills = normalize_skills(resume_skills)

    resume_skill_map = {skill.lower(): skill for skill in clean_resume_skills}

    matched = [skill for skill in required_skills if skill.lower() in resume_skill_map]

    missing = [
        skill for skill in required_skills if skill.lower() not in resume_skill_map
    ]

    if required_skills:
        score = round(
            len(matched) / len(required_skills) * 100,
            2,
        )

    else:
        score = 0

    return score, matched, missing
