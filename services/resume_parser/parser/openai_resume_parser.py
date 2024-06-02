import openai
from openai import OpenAI
import json

import os
from pdfminer.high_level import extract_text

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def parse_resume_json(resume_text, links=None):
    
    prompt = f"""
    Extract the following information from the resume text.
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
            - location
        - education 2 similar to above and so on
    - Work Experience (this can include internships, etc.)
        - experience 1
            - organization
            - position
            - role description
            - start date (format: MM/YYYY)
            - end date (format: MM/YYYY or "Present" if currently working)
            - location
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
    {links}


    Also, extract any additional information that you think is relevant and not covered in the above points.
    Use the exact keys and sub-key etc naming convention as described above. 
    If the information is not present in the resume then set the value to an empty string or null-value.
    If skills are not found or clearly incicated by a heading, then pick the skills as per the resume.
    Provide the extracted information in JSON format. Return only the JSON string.
    """

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a resume information extractor. You have been provided with the data in the resume and your job is to understand the data and extract the required information."},
            {"role": "system", "content": "When given the resume text, process and understand the data throughly and then proceed to present the extracted information in JSON format."},
            {"role": "user", "content": prompt}
        ],
        stop=None,
    )

    raw_response = response.choices[0].message.content
    
    start_idx = raw_response.find("{")
    end_idx = raw_response.rfind("}")
    

    try:
        json_data = json.loads(raw_response[start_idx:end_idx+1])
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        raise
    
    return json_data

