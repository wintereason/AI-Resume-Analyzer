import fitz


def extract_text_from_pdf(pdf_path):

    text = ""

    try:

        doc = fitz.open(pdf_path)


        for page_number, page in enumerate(doc):

            page_text = page.get_text()

            text += page_text + "\n"


        doc.close()

        return text


    except Exception as e:

        print("Error while reading PDF:", e)

        return None



# Testing

if __name__ == "__main__":

    pdf_file = "Upload/Resume.pdf"


    resume_text = extract_text_from_pdf(pdf_file)


    if resume_text:

        print("------ RESUME TEXT ------")
        print(resume_text)

    else:

        print("No text extracted")