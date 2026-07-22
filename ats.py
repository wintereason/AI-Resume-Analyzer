def calculate_ats_score(candidate_skills, required_skills):

    matched = []
    missing = []

    candidate = [skill.lower() for skill in candidate_skills]

    for skill in required_skills:

        if skill.lower() in candidate:
            matched.append(skill)
        else:
            missing.append(skill)

    if len(required_skills) == 0:
        score = 0
    else:
        score = int((len(matched) / len(required_skills)) * 100)

    return score, matched, missing