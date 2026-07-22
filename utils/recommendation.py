from database import get_connection


def recommend_jobs(resume_skills):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            jr.job_role_id,
            jr.job_title,
            jr.average_salary_india,
            jr.average_salary_us,
            jr.demand_level,
            s.skill_name

        FROM job_roles jr

        JOIN job_role_skills jrs
        ON jr.job_role_id = jrs.job_role_id

        JOIN skills s
        ON jrs.skill_id = s.skill_id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    jobs = {}

    for row in rows:

        title = row["job_title"]

        if title not in jobs:

            jobs[title] = {
                "india_salary": row["average_salary_india"],
                "us_salary": row["average_salary_us"],
                "demand": row["demand_level"],
                "required": [],
                "matched": []
            }

        jobs[title]["required"].append(row["skill_name"])

    # Compare skills
    resume_skills = [s.lower() for s in resume_skills]

    recommendations = []

    for title, info in jobs.items():

        required = [s.lower() for s in info["required"]]

        matched = [
            skill for skill in required
            if skill in resume_skills
        ]

        missing = [
            skill for skill in required
            if skill not in resume_skills
        ]

        score = int(
            (len(matched) / len(required)) * 100
        )

        recommendations.append({

            "job": title,
            "score": score,
            "matched": matched,
            "missing": missing,
            "salary_india": info["india_salary"],
            "salary_us": info["us_salary"],
            "demand": info["demand"]

        })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations[:3]