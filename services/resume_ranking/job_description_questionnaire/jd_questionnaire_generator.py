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
    The questionnaire will evaluate candidate resumes by examining key qualifications, skills, career experiences, and overall fit for the role.
    The goal is to ensure comprehensive evaluation while minimizing subconscious bias by avoiding personal information such as names, gender, or other identifiers.

    The questionnaire should be comprehensive and broken down into the following categories, with clear and structured questions.
    Pay close attention to ensure that each question is targeted, relevant, and aligned with the requirements mentioned in the job description.

    1. **Core Job Skills:**  
    - **Instruction:** Build questions that assess both essential technical and soft skills like problem-solving and teamwork.
      Ensure that each question specifically relates to the critical skills mentioned in the job description, with appropriate weightings reflecting their importance.  
    - Example: Does the candidate have experience with [specific technical skill]?  
    - Structure each question to focus on how well the candidate demonstrates proficiency and relevance to the role.

    2. **Work History:**  
    - **Instruction:** Create questions that examine the candidate's career trajectory, job role consistency, required years of experience and the relevancy of past employers.
      Consider the duration spent in each role, any promotions or lateral moves, and how non-linear career paths (such as gaps) may represent development rather than red flags.
      Ensure these questions accommodate different career paths.  
    - Example: Has the candidate shown progression through promotions or changes in job titles?

    3. **Education and Certifications:**  
    - **Instruction:** Formulate questions that evaluate the candidate’s degrees, certifications, and relevance to the role.
      Ensure that these questions check for the recognition of the institution and alignment with the job requirements.  
    - Example: Does the candidate hold certifications that are directly related to the job description's technical requirements?

    4. **Location and Work Eligibility:**  
    - **Instruction:** Ask questions to assess the candidate’s current location, their eligibility to work in the specified location, and their willingness to relocate.  
    - Example: Is the candidate currently located within or willing to relocate to the region specified in the job description?

    5. **Industry and Domain Expertise:**  
    - **Instruction:** Build questions that assess the candidate’s years of experience in relevant industries or domains.
      Include questions that check whether they’ve worked with large or well-known companies, ensuring cultural fit and the ability to handle workload and expectations.  
    - Example: Has the candidate worked in [specific industry/domain] for the required number of years?

    6. **Transferable Skills:**  
    - **Instruction:** Form questions to assess whether the candidate has skills that can be applied to the role, even if not explicitly mentioned in the job description.
      Highlight how emerging technologies or experiences in related fields may be valuable to the role.  
    - Example: Does the candidate possess transferable skills in areas like cloud services (e.g., AWS vs. Azure)?

    7. **Career Impact and Initiative:**  
    - **Instruction:** Formulate questions that assess the candidate’s leadership roles, awards, or initiatives they’ve led that impacted their previous organizations.
      These questions should aim to understand the candidate’s potential for growth in the role.  
    - Example: Has the candidate led any projects or initiatives that had a significant impact on their previous employers?

    8. **Language Proficiency:**  
    - **Instruction:** Ensure the questions evaluate whether the candidate has the language skills required for the role.  
    - Example: Does the candidate have proficiency in [specific language] as required for the role?

    9. **Cultural Fit and Adaptability:**  
    - **Instruction:** Create questions that assess the candidate’s ability to collaborate with teams, take on mentorship roles, and adapt to new environments or changes within organizations.
      Focus on how the candidate has handled challenges like learning new systems or adapting to company restructuring.  
    - Example: How well has the candidate adapted to changes in their previous roles, such as learning new systems or dealing with major organizational shifts?

    10. **Diversity and Inclusion:**  
    - **Instruction:** Develop questions that evaluate the candidate’s experience working in diverse teams and contributing to inclusive work environments.
      These questions should ensure that the candidate values and promotes diversity.  
    - Example: Has the candidate worked in diverse teams and contributed to fostering an inclusive work environment?

    Weighting Guidelines:

    For each question, assign a weight on a scale of 1-5, where:
    - 5: Indicates a **critical** question that is absolutely essential for the role and should strongly influence the evaluation of the candidate.
    - 4: Indicates an **important** question that, while not critical, plays a significant role in assessing the candidate’s fit.
    - 3: Indicates a **moderately important** question that provides useful insights but may not be a strict requirement.
    - 2: Indicates a **nice-to-have** question that adds value but is not a key factor in deciding the candidate’s fit.
    - 1: Indicates a **low-priority** question that provides supplementary information but has little impact on the evaluation.

    Additional considerations:
    - Avoid using the candidate's name, gender, or personal details to reduce subconscious bias, and ensure that the questionnaire avoids bias in relation to age, race, or other personal preferences.
    - Compare educational and work history with job requirements. Focus on consistency in the career path, noting changes in position (e.g., progressive, lateral, or random job changes).
    - Watch for red flags like frequent job hopping, stagnation in roles, incomplete or inconsistent information, and careless mistakes in the resume.
    - Pay attention to whether past employment is in line with the role and industry, looking for a pattern rather than randomness in job history.

    The responses should be formatted in JSON, with each question categorized and structured as follows:
    - The main key should be "questionnaire".
    - Inside "questionnaire", each category (e.g., "Core Job Skills", "Work History") should have its own section.
    - Each question should be formatted as:
        - "question": [The specific question that assesses the requirement, addressing the candidate for example "Does the candidate have experience with...?"]
        - "weight": [The importance of the question on a scale of 1-5, based on the weighting guidelines above]
        - "scoring": [leave it blank with quotes so that it can be filler after evaluating a candidate]

    Here is the job description:
    {job_description}

    Generate a robust questionnaire covering all aspects of the job description, paying close attention to every tiny detail, from technical skills, non-technical skills to cultural fit and career consistency.
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
