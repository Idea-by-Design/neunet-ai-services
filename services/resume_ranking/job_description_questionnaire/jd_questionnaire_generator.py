import os
import openai
from openai import OpenAI
import json


openai.api_key = 'sk-WVMOT-ux9F3MYCBpJdCTqCwjPfyCQa-iGBwD7yJtkST3BlbkFJyDQSA4BntLqFwINg-xRxS3DAsAbTbvlH5Cs2iUr2EA'
client = OpenAI(api_key='sk-WVMOT-ux9F3MYCBpJdCTqCwjPfyCQa-iGBwD7yJtkST3BlbkFJyDQSA4BntLqFwINg-xRxS3DAsAbTbvlH5Cs2iUr2EA')

# Function to generate a questionnaire using GPT-4o-mini
def generate_questionnaire(job_description):
    prompt = f"""
    You are an expert recruitment consultant. Your task is to create a detailed questionnaire based on the provided job description. 
    The questionnaire will evaluate candidate resumes by examining key qualifications, skills, and career experiences. The questionnaire should be comprehensive and broken down into the following categories:

    1. **Core Job Skills**: Questions about the essential technical and soft skills required for the role.
    2. **Work History**: Questions about career trajectory, consistency in job roles, and relevant past employers.
    3. **Education and Certifications**: Questions to check the relevance of degrees, certifications, and any required training.
    4. **Location and Work Eligibility**: Questions about the candidate's current location, willingness to relocate, and eligibility to work in the specified location.
    5. **Industry and Domain Expertise**: Questions assessing years of experience, industry exposure, and familiarity with the domain.
    6. **Transferable Skills**: Questions on whether a candidate has skills from related technologies or industries that can be applied to the job (e.g., AWS vs. Azure).
    7. **Career Impact and Initiative**: Questions evaluating leadership experience, awards, promotions, and any initiatives taken that have impacted past roles.
    8. **Language Proficiency**: Questions to verify any language skills required for the role.
    9. **Cultural Fit**: Questions about the candidate's team collaboration, mentorship roles, and adaptability.

    The responses should be in JSON format, with each question containing the following structure:    
    - The main key should be "questionnaire".
    - Inside "questionnaire", each category (e.g., "Core Job Skills", "Work History") should be a separate section.
    - Each question should be formatted as:
        - "question": [The specific question that assesses the requirement and addresses the candidate as Does the candidate have experience with...?"]
        - "weight": [The importance of the question on a scale of 1-5]
        - "scoring": [A scoring guide, e.g., 2 points for direct experience, 1 point for transferable skills, 0 points for no experience.]


    Here is the job description:
    {job_description}
    
    Generate a robust questionnaire covering all aspects of the job description, paying attention to every tiny detail of the role, from technical skills to cultural fit.

    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert recruitment consultant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # Controlled randomness
        max_tokens=2000  # Adjust based on expected response length
    )

    return completion.choices[0].message.content.strip()

# Function to save the generated LLM response in a plain text file
def save_questionnaire(questionnaire, output_folder, output_filename):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_path = os.path.join(output_folder, output_filename)

    # Save the LLM response to a plain text file
    with open(output_path, 'w') as txt_file:
        txt_file.write(questionnaire)

    return output_path
