import re
from utils.skill_fetch import get_all_skills


# Extract Email
def extract_email(text="aarav.sharma@gmail.com"):

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    email = re.findall(email_pattern, text)

    if email:
        return email[0]

    return None



# Extract Phone Number
def extract_phone(text):

    phone_pattern = r"(?:\+91[-\s]?)?[6-9]\d{4}[-\s]?\d{5}"

    match = re.search(phone_pattern, text)

    if match:
        phone = match.group()
        phone = phone.replace(" ", "").replace("-", "")
        return phone

    return None



# Extract Name
def extract_name(text="Aarav Sharma"):

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if line:
            return line

    return None



# Extract Skills
def extract_skills(text):

    skills_list = get_all_skills()

    found_skills = []

    for skill in skills_list:

        if skill.lower() in text.lower():

            found_skills.append(skill)

    return found_skills



# Extract Education
def extract_education(text):

    education_keywords = [
        "B.Tech",
        "Bachelor",
        "B.E",
        "M.Tech",
        "Master",
        "12th",
        "10th"
    ]

    education = []

    for word in education_keywords:

        if word.lower() in text.lower():
            education.append(word)

    return education



# Extract Projects
def extract_projects(text):

    projects = []

    lines = text.split("\n")

    collecting = False

    for line in lines:

        line = line.strip()

        if line.upper().startswith("PROJECTS"):
            collecting = True
            continue

        if collecting:

            if line == "":
                continue

            # Stop when another section starts
            if line.isupper():
                break

            # Format 1: Project 1: Resume Parser using Python
            if line.lower().startswith("project"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    projects.append(parts[1].strip())
                continue

            # Format 2: Ignore bullet points
            if line.startswith("•"):
                continue

            # Format 2: Project title
            projects.append(line)

    return projects

if __name__ == "__main__":

    resume_text = """
    Aarav Sharma

    Email: aarav.sharma@gmail.com

    Phone: 9876543210

    Education:
    B.Tech Computer Science

    Skills:
    Python
    SQL
    Machine Learning

    Projects:
    Project 1: Resume Parser using Python
    Project 2: AI Chatbot using NLP
    """


    print("Name:", extract_name(resume_text))

    print("Email:", extract_email(resume_text))

    print("Phone:", extract_phone(resume_text))

    print("Skills:", extract_skills(resume_text))

    print("Education:", extract_education(resume_text))

    print("Projects:", extract_projects(resume_text))