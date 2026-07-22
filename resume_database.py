from database import get_connection
from utils.activity_manager import add_candidate_activity


def convert_to_text(value):
    """
    Convert list-like values into database-safe text.
    """

    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item).strip() for item in value if str(item).strip())

    return str(value or "").strip()


def save_resume(resume_data):
    """
    Save resume information, including the PDF file path,
    and create the first activity timeline record.
    """

    connection = get_connection()
    cursor = connection.cursor()

    resume_id = None

    try:
        query = """
        INSERT INTO resumes (
            name,
            email,
            phone,
            education,
            skills,
            projects,
            ats_score,
            recommended_role,
            status,
            resume_file
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        """

        candidate_status = resume_data.get("status") or "Under Review"

        recommended_role = resume_data.get("recommended_role") or "Not Assigned"

        ats_score = resume_data.get(
            "ats_score",
            0,
        )

        resume_file = convert_to_text(resume_data.get("resume_file"))

        values = (
            resume_data.get("name", ""),
            resume_data.get("email", ""),
            resume_data.get("phone", ""),
            convert_to_text(resume_data.get("education", [])),
            convert_to_text(resume_data.get("skills", [])),
            convert_to_text(resume_data.get("projects", [])),
            ats_score,
            recommended_role,
            candidate_status,
            resume_file or None,
        )

        cursor.execute(query, values)

        resume_id = cursor.lastrowid

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    try:
        add_candidate_activity(
            candidate_id=resume_id,
            performed_by=resume_data.get("performed_by"),
            activity_type="resume_uploaded",
            activity_title="Resume uploaded and analysed",
            activity_description=(
                f"Resume saved with an ATS score of "
                f"{ats_score}% and recommended role "
                f"{recommended_role}."
            ),
            old_status=None,
            new_status=candidate_status,
        )

    except Exception as activity_error:
        print(
            "Candidate saved, but activity could not " f"be recorded: {activity_error}"
        )

    return resume_id
