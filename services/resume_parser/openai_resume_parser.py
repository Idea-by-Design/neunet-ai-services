import openai
from openai import OpenAI

import os
from pdfminer.high_level import extract_text

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def parse_resume(file_path):
    resume_text = extract_text(file_path)
    
    prompt = f"""
    Extract the following information from the resume text:
    - Name
    - Email
    - Secondary Email
    - Phone Number
    - Secondary Phone Number
    - Location
    - Links 
        - LinkedIn
        - GitHub
        - Website
        - Other
    - Skills (comma-separated list)
    - Education 
        - education 1 
            - degree
            - institute
            - major
            - minor
            - start (format: MM/YYYY)
            - end (format: MM/YYYY or "Present" if currently enrolled)
        - education 2 similar to above and so on
    - Work Experience (this can include internships, etc.)
        - experience 1
            - organization
            - position
            - role description
            - start date (format: MM/YYYY)
            - end date (format: MM/YYYY or "Present" if currently working)
        - experience 2 similar to above and so on
    - Projects
        - project 1
            - title
            - description
        - project 2 similar to above and so on
    - Co-curricular activities
    - Publications 
        - publication 1
            - title
            - link,
            - description
        - publication 2 similar to above and so on
    - Achievements

    Resume Text:
    {resume_text}

    Provide the extracted information in JSON format. If the information is not present in the resume then set the value to None.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a resume information extractor"},
            {"role": "user", "content": prompt}
        ],
        stop=None,
    )

    return response['choices'][0]['message']['content'].strip()
