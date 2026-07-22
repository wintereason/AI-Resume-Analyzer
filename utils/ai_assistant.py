import re

from database import get_connection


# ---------------------------------
# Get All Candidates
# ---------------------------------
def get_all_candidates():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            skills,
            ats_score,
            recommended_role,
            status
        FROM resumes
    """)

    candidates = cursor.fetchall()

    cursor.close()
    conn.close()

    return candidates


# ---------------------------------
# Search Candidates by Skill
# ---------------------------------
def search_by_skill(skill):

    candidates = get_all_candidates()

    results = []

    for candidate in candidates:

        skills = candidate["skills"].lower()

        if skill.lower() in skills:

            results.append(candidate)

    return results


# ---------------------------------
# Highest ATS Candidate
# ---------------------------------
def highest_ats():

    candidates = get_all_candidates()

    if not candidates:
        return None

    return max(candidates, key=lambda x: float(x["ats_score"] or 0))


# ---------------------------------
# ATS Above Threshold
# ---------------------------------
def ats_above(score):

    candidates = get_all_candidates()

    results = []

    for candidate in candidates:

        if float(candidate["ats_score"] or 0) >= score:

            results.append(candidate)

    return results


# ---------------------------------
# Search by Recommended Role
# ---------------------------------
def search_by_role(role):

    candidates = get_all_candidates()

    results = []

    for candidate in candidates:

        job = str(candidate["recommended_role"]).lower()

        if role.lower() in job:

            results.append(candidate)

    return results


# ---------------------------------
# Missing Skill
# ---------------------------------
def missing_skill(skill):

    candidates = get_all_candidates()

    results = []

    for candidate in candidates:

        skills = candidate["skills"].lower()

        if skill.lower() not in skills:

            results.append(candidate)

    return results


# ---------------------------------
# Intent Detection
# ---------------------------------
def answer_question(question):

    question = question.lower()

    # Highest ATS
    if "highest ats" in question or "best ats" in question:

        return ("highest_ats", highest_ats())

    # ATS above 80
    match = re.search(r"above\s+(\d+)", question)

    if match:

        score = int(match.group(1))

        return ("ats_above", ats_above(score))

    # Python developers
    if "python" in question:

        return ("skill", search_by_skill("Python"))

    if "sql" in question:

        return ("skill", search_by_skill("SQL"))

    if "machine learning" in question:

        return ("skill", search_by_skill("Machine Learning"))

    if "power bi" in question:

        return ("skill", search_by_skill("Power BI"))

    if "java" in question:

        return ("skill", search_by_skill("Java"))

    if "git" in question:

        return ("skill", search_by_skill("Git"))

    # Job Roles
    if "data analyst" in question:

        return ("role", search_by_role("Data Analyst"))

    if "python developer" in question:

        return ("role", search_by_role("Python Developer"))

    if "machine learning engineer" in question:

        return ("role", search_by_role("Machine Learning Engineer"))

    # Missing Skills
    if "missing docker" in question:

        return ("missing", missing_skill("Docker"))

    if "missing git" in question:

        return ("missing", missing_skill("Git"))

    if "missing power bi" in question:

        return ("missing", missing_skill("Power BI"))

    return ("unknown", None)
