from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet



def generate_pdf(
        resume_data,
        recommendations,
        feedback,
        matched,
        missing
):

    filename = "ATS_Report.pdf"


    doc = SimpleDocTemplate(
        filename
    )


    styles = getSampleStyleSheet()

    story = []


    # Title

    story.append(
        Paragraph(
            "🤖 AI Resume Analyzer Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1,12)
    )


    # Candidate Details

    story.append(
        Paragraph(
            "<b>Candidate Information</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Paragraph(
            f"Name: {resume_data['name']}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Email: {resume_data['email']}",
            styles["BodyText"]
        )
    )


    story.append(
        Paragraph(
            f"Phone: {resume_data['phone']}",
            styles["BodyText"]
        )
    )


    story.append(Spacer(1,12))


    # ATS Score

    story.append(
        Paragraph(
            "<b>ATS Analysis</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Paragraph(
            f"ATS Score: {resume_data['ats_score']}%",
            styles["BodyText"]
        )
    )


    story.append(
        Paragraph(
            f"Resume Rating: {feedback['rating']}/10",
            styles["BodyText"]
        )
    )


    story.append(Spacer(1,12))


    # Skills

    story.append(
        Paragraph(
            "<b>Skills</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Paragraph(
            ", ".join(resume_data["skills"]),
            styles["BodyText"]
        )
    )


    story.append(Spacer(1,12))


    # Matched Skills

    story.append(
        Paragraph(
            "<b>Matched Skills</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Paragraph(
            ", ".join(matched),
            styles["BodyText"]
        )
    )



    # Missing Skills

    story.append(
        Paragraph(
            "<b>Missing Skills</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Paragraph(
            ", ".join(missing),
            styles["BodyText"]
        )
    )



    # AI Feedback

    story.append(
        Paragraph(
            "<b>AI Resume Feedback</b>",
            styles["Heading2"]
        )
    )


    story.append(
        Paragraph(
            "Strengths:",
            styles["BodyText"]
        )
    )


    for item in feedback["strengths"]:

        story.append(
            Paragraph(
                "✔ " + item,
                styles["BodyText"]
            )
        )


    story.append(
        Paragraph(
            "Suggestions:",
            styles["BodyText"]
        )
    )


    for item in feedback["suggestions"]:

        story.append(
            Paragraph(
                "➤ " + item,
                styles["BodyText"]
            )
        )


    # Job Recommendations

    story.append(
        Paragraph(
            "<b>Recommended Jobs</b>",
            styles["Heading2"]
        )
    )


    for job in recommendations:

        story.append(
            Paragraph(
                f"{job['job']} - {job['score']}%",
                styles["BodyText"]
            )
        )


    doc.build(story)


    return filename