from ai_resume_analyzer.resume_parser import extract_text_from_pdf
from ai_resume_analyzer.resume_database import save_resume
from ai_resume_analyzer.extractor import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    extract_education,
    extract_projects
)

resume_path = r"Upload\resume.pdf"

text = extract_text_from_pdf(resume_path)

if text:

    # Store extracted information in a dictionary
    resume_data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "projects": extract_projects(text)
    }

    # Save to MySQL
    save_resume(resume_data)

    print("========== RESUME DETAILS ==========\n")

    print("Name:", resume_data["name"])
    print("Email:", resume_data["email"])
    print("Phone:", resume_data["phone"])
    print("Skills:", resume_data["skills"])
    print("Education:", resume_data["education"])
    print("Projects:", resume_data["projects"])

else:
    print("No text extracted.")