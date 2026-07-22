from collections import Counter

from database import get_connection


# ---------------------------------
# Analytics Summary
# ---------------------------------
def get_analytics():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(AVG(ats_score), 0) AS average,
                COALESCE(MAX(ats_score), 0) AS highest,
                COALESCE(MIN(ats_score), 0) AS lowest
            FROM resumes
            WHERE ats_score IS NOT NULL
            """)

        result = cursor.fetchone()

        if not result:
            return {
                "total": 0,
                "average": 0,
                "highest": 0,
                "lowest": 0,
            }

        return {
            "total": result.get("total", 0) or 0,
            "average": round(
                float(result.get("average", 0) or 0),
                2,
            ),
            "highest": round(
                float(result.get("highest", 0) or 0),
                2,
            ),
            "lowest": round(
                float(result.get("lowest", 0) or 0),
                2,
            ),
        }

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# ATS Score Distribution
# ---------------------------------
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
                COUNT(*) AS candidate_count
            FROM resumes
            WHERE ats_score IS NOT NULL
            GROUP BY score_range
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Candidate Status Distribution
# ---------------------------------
def get_candidate_status_distribution():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                COALESCE(
                    NULLIF(status, ''),
                    'Not Assigned'
                ) AS status,
                COUNT(*) AS candidate_count
            FROM resumes
            GROUP BY status
            ORDER BY candidate_count DESC
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Job Role Distribution
# ---------------------------------
def get_job_role_distribution():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                COALESCE(
                    NULLIF(recommended_role, ''),
                    'Not Assigned'
                ) AS recommended_role,
                COUNT(*) AS candidate_count
            FROM resumes
            GROUP BY recommended_role
            ORDER BY candidate_count DESC
            LIMIT 10
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Top Skills
# ---------------------------------
def get_top_skills(limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT skills
            FROM resumes
            WHERE skills IS NOT NULL
            AND skills != ''
            """)

        rows = cursor.fetchall()

        skill_counter = Counter()

        for row in rows:
            skills_text = row[0]

            if not skills_text:
                continue

            candidate_skills = set()

            for skill in skills_text.split(","):
                cleaned_skill = skill.strip()

                if cleaned_skill:
                    candidate_skills.add(cleaned_skill.title())

            skill_counter.update(candidate_skills)

        return [
            {
                "skill": skill,
                "candidate_count": count,
            }
            for skill, count in skill_counter.most_common(limit)
        ]

    finally:
        cursor.close()
        connection.close()


# ---------------------------------
# Top Candidates
# ---------------------------------
def get_top_candidates(limit=10):
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
            ORDER BY ats_score DESC, id DESC
            LIMIT %s
            """,
            (limit,),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()
