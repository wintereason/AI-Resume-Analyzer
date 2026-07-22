def generate_feedback(resume_data):

    strengths = []
    suggestions = []

    score = 0


    # Skills analysis
    skills = resume_data.get("skills", [])

    if len(skills) >= 5:
        strengths.append(
            "Good technical skill coverage"
        )
        score += 2

    else:
        suggestions.append(
            "Add more technical skills related to your target role"
        )


    # Projects analysis
    projects = resume_data.get("projects", [])

    if len(projects) >= 2:
        strengths.append(
            "Projects section is present"
        )
        score += 2

    else:
        suggestions.append(
            "Add more real-world projects with descriptions"
        )


    # Education analysis
    education = resume_data.get("education", [])

    if education:
        strengths.append(
            "Educational background is mentioned"
        )
        score += 1

    else:
        suggestions.append(
            "Add your education details"
        )


    # Contact details
    if resume_data.get("email"):
        strengths.append(
            "Contact information available"
        )
        score += 1

    else:
        suggestions.append(
            "Add professional contact details"
        )


    # ATS Score
    ats = resume_data.get(
        "ats_score",
        0
    )

    if ats >= 80:

        strengths.append(
            "High ATS compatibility"
        )

        score += 2

    elif ats < 60:

        suggestions.append(
            "Improve ATS score by adding missing skills"
        )


    rating = min(
        score + 2,
        10
    )


    return {

        "rating": rating,
        "strengths": strengths,
        "suggestions": suggestions

    }