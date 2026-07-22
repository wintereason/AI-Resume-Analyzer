import random

from database import get_connection

# ---------------------------------
# Interview Question Banks
# ---------------------------------
SKILL_QUESTIONS = {
    "python": [
        "What is the difference between a list and a tuple in Python?",
        "Explain exception handling in Python.",
        "What are Python decorators?",
        "What is the difference between shallow copy and deep copy?",
        "How would you improve a slow Python program?",
    ],
    "sql": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain database normalization.",
        "What is the difference between WHERE and HAVING?",
        "How would you find duplicate records in SQL?",
        "What are database indexes?",
    ],
    "machine learning": [
        "What is the difference between supervised and unsupervised learning?",
        "What is overfitting, and how can it be prevented?",
        "How do you evaluate a classification model?",
        "What is feature engineering?",
        "What is cross-validation?",
    ],
    "data science": [
        "How do you approach a new data-science problem?",
        "How do you handle missing values?",
        "What steps are involved in exploratory data analysis?",
        "How do you detect outliers?",
        "What is the difference between correlation and causation?",
    ],
    "pandas": [
        "What is the difference between loc and iloc?",
        "How do you handle missing data in Pandas?",
        "How do you merge two DataFrames?",
        "How do you group and aggregate data?",
        "How do you remove duplicate rows?",
    ],
    "numpy": [
        "Why is NumPy faster than Python lists?",
        "What is NumPy broadcasting?",
        "What is vectorization?",
        "What is the difference between reshape and resize?",
        "How do you perform element-wise operations?",
    ],
    "power bi": [
        "What is the difference between a measure and a calculated column?",
        "What is DAX?",
        "How do relationships work in Power BI?",
        "How would you design a management dashboard?",
        "How do you optimize a slow Power BI report?",
    ],
    "git": [
        "What is the difference between Git merge and rebase?",
        "How do you resolve a merge conflict?",
        "What is the purpose of Git branches?",
        "What is the difference between Git fetch and pull?",
        "How would you undo a recent commit?",
    ],
    "java": [
        "Explain the main principles of object-oriented programming.",
        "What is the difference between overloading and overriding?",
        "What is the difference between an interface and an abstract class?",
        "How does exception handling work in Java?",
        "How does Java memory management work?",
    ],
    "html": [
        "What is semantic HTML?",
        "What is the difference between block and inline elements?",
        "How do HTML forms work?",
        "What are meta tags?",
        "How can webpage accessibility be improved?",
    ],
    "css": [
        "What is the CSS box model?",
        "What is the difference between Flexbox and Grid?",
        "What is CSS specificity?",
        "How do media queries work?",
        "What is the difference between relative and absolute positioning?",
    ],
    "streamlit": [
        "What is st.session_state used for?",
        "How do you create a multi-page Streamlit application?",
        "How do you connect Streamlit to MySQL?",
        "How does Streamlit rerun an application?",
        "How would you improve Streamlit application performance?",
    ],
}


GENERAL_QUESTIONS = [
    "Tell me about a technical project you are most proud of.",
    "Describe a difficult technical problem you solved.",
    "How do you test and debug your code?",
    "How do you learn a new programming tool or framework?",
    "Describe a situation where you worked as part of a team.",
    "How do you manage multiple tasks with tight deadlines?",
    "What improvements would you make to your latest project?",
    "Why are you suitable for this role?",
]


ROLE_QUESTIONS = {
    "data analyst": [
        "How would you investigate a sudden decline in monthly sales?",
        "Which KPIs would you include in a business dashboard?",
    ],
    "machine learning engineer": [
        "How would you deploy a machine-learning model?",
        "How would you monitor model performance after deployment?",
    ],
    "python developer": [
        "How would you structure a large Python application?",
        "How would you test a Python API?",
    ],
    "web developer": [
        "How would you improve a slow web application?",
        "How do you make a website responsive and accessible?",
    ],
}


# ---------------------------------
# Helper Functions
# ---------------------------------
def normalize_list(value):
    if value is None:
        return []

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]

    return [str(value).strip()]


# ---------------------------------
# Get Required Skills for Job Role
# ---------------------------------
def get_job_skills(job_role_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT s.skill_name
        FROM skills s
        JOIN job_role_skills jrs
            ON s.skill_id = jrs.skill_id
        WHERE jrs.job_role_id = %s
        """

        cursor.execute(
            query,
            (job_role_id,),
        )

        skills = cursor.fetchall()

        return [skill["skill_name"] for skill in skills]

    finally:
        cursor.close()
        conn.close()


# ---------------------------------
# Match Candidates with Required Skills
# ---------------------------------
def match_candidates(required_skills):
    required_skills = normalize_list(required_skills)

    if not required_skills:
        return []

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
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

    finally:
        cursor.close()
        conn.close()

    normalized_required_skills = {skill.lower(): skill for skill in required_skills}

    results = []

    for candidate in candidates:
        resume_skills = normalize_list(candidate.get("skills"))

        normalized_resume_skills = {skill.lower() for skill in resume_skills}

        matched = [
            original_skill
            for normalized_skill, original_skill in normalized_required_skills.items()
            if normalized_skill in normalized_resume_skills
        ]

        missing = [
            original_skill
            for normalized_skill, original_skill in normalized_required_skills.items()
            if normalized_skill not in normalized_resume_skills
        ]

        score = round(
            len(matched) / len(required_skills) * 100,
            2,
        )

        results.append(
            {
                "id": candidate.get("id"),
                "name": candidate.get("name"),
                "email": candidate.get("email"),
                "phone": candidate.get("phone"),
                "skills": resume_skills,
                "match_score": score,
                "ats_score": candidate.get("ats_score") or 0,
                "recommended_role": (
                    candidate.get("recommended_role") or "Not Assigned"
                ),
                "status": (candidate.get("status") or "Under Review"),
                "matched_skills": matched,
                "missing_skills": missing,
            }
        )

    results.sort(
        key=lambda item: (
            item["match_score"],
            float(item["ats_score"] or 0),
        ),
        reverse=True,
    )

    return results


# ---------------------------------
# Recruiter Summary
# ---------------------------------
def generate_recruiter_summary(
    candidate_name,
    skills,
    ats_score,
    recommended_role,
    match_score=0,
    education="",
    projects="",
):
    clean_skills = normalize_list(skills)

    top_skills = clean_skills[:5]

    skills_text = (
        ", ".join(top_skills) if top_skills else "limited identified technical skills"
    )

    try:
        ats_score = float(ats_score or 0)

    except (TypeError, ValueError):
        ats_score = 0

    try:
        match_score = float(match_score or 0)

    except (TypeError, ValueError):
        match_score = 0

    if ats_score >= 80:
        ats_description = "a strong ATS-compatible resume"

    elif ats_score >= 60:
        ats_description = "a moderately ATS-compatible resume"

    else:
        ats_description = "a resume that requires further improvement"

    project_text = str(projects or "").strip()

    if project_text:
        project_sentence = (
            "The resume also contains project experience "
            "that should be discussed during the interview."
        )

    else:
        project_sentence = (
            "The candidate should provide more detailed "
            "project examples during the interview."
        )

    return (
        f"{candidate_name} demonstrates skills in {skills_text}. "
        f"The candidate has {ats_description}, with an ATS score "
        f"of {ats_score:.1f}%. The strongest recommended role is "
        f"{recommended_role}, with an estimated {match_score:.1f}% "
        f"skill match. {project_sentence}"
    )


# ---------------------------------
# Interview Question Generator
# ---------------------------------
def generate_interview_questions(
    skills,
    job_role="",
    number_of_questions=8,
):
    clean_skills = normalize_list(skills)

    question_pool = []

    for skill in clean_skills:
        normalized_skill = skill.lower().strip()

        if normalized_skill in SKILL_QUESTIONS:
            question_pool.extend(SKILL_QUESTIONS[normalized_skill])

    normalized_role = str(job_role or "").lower().strip()

    if normalized_role in ROLE_QUESTIONS:
        question_pool.extend(ROLE_QUESTIONS[normalized_role])

    question_pool.extend(GENERAL_QUESTIONS)

    unique_questions = list(dict.fromkeys(question_pool))

    random.shuffle(unique_questions)

    return unique_questions[:number_of_questions]
