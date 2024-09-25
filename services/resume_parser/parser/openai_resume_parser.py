import openai
from openai import OpenAI
import json

import os


openai.api_key = 'sk-WVMOT-ux9F3MYCBpJdCTqCwjPfyCQa-iGBwD7yJtkST3BlbkFJyDQSA4BntLqFwINg-xRxS3DAsAbTbvlH5Cs2iUr2EA'
client = OpenAI(api_key='sk-WVMOT-ux9F3MYCBpJdCTqCwjPfyCQa-iGBwD7yJtkST3BlbkFJyDQSA4BntLqFwINg-xRxS3DAsAbTbvlH5Cs2iUr2EA')


def parse_resume_json(resume_text, links=None):
    
    prompt = f"""
    Extract the following information from the resume text.
    - name 
    - email
    - secondary email
    - phone number
    - secondary phone number
    - location
    - links 
        - linkedIn
        - gitHub
        - website
        - other
    - skills (comma-separated list)
    - education 
        - education 1 
            - degree
            - institute
            - major
            - minor
            - start (format: MM/YYYY)
            - end (format: MM/YYYY or "Present" if currently enrolled)
            - location
        - education 2 similar to above and so on
    - work experience (this can include internships, etc.)
        - experience 1
            - organization
            - position
            - role description
            - start date (format: MM/YYYY)
            - end date (format: MM/YYYY or "Present" if currently working)
            - location
        - experience 2 similar to above and so on
    - projects
        - project 1
            - title
            - description
        - project 2 similar to above and so on
    - co-curricular activities
    - publications 
        - publication 1
            - title
            - link,
            - description
        - publication 2 similar to above and so on
    - achievements
    - certifications
    - references
    - languages
    - hobbies
    - keywords (comma-separated list; analyse the resume text to detect technical and non-technical skills of the candidate and  tools, technologies, etc. the candidate appears to be proficient in; list should be exhaustive)

    Resume Text:
    {resume_text}
    {links}


    Also, extract any additional information that you think is relevant and not covered in the above points.
    Use the exact keys and sub-key etc naming convention as described above. 
    If the information is not present in the resume then set the value to an empty string or null-value.
    If skills are not found or clearly incicated by a heading, then pick the skills as per the resume and add them to "keywords" tag.
    "keywordes" tag cannot be empty. Analyse the resume to best of your ability and provide the keywords. Make sure to include both technical and non-technical skills. Examples of non-technical skills are leadership, time management, planning, decision making, strategic thinking etc). Be exhaustive.
    Provide the extracted information in JSON format. Return only the JSON string.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
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

