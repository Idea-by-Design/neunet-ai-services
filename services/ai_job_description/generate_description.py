import openai
from openai import OpenAI
import os
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def generate_description(data):
    # Load the initial prompt template
    prompt_template = load_prompt()

    # Fill in missing fields with defaults if necessary
    data = fill_missing_fields_with_defaults(data)

    # Check for missing fields (for interactive gathering if needed)
    missing_fields = check_missing_fields(data)
    if missing_fields:
        # Generate questions for missing fields
        questions = generate_questions_for_missing_fields(missing_fields)
        
        # Gather missing information via a more complex method (e.g., API call, chatbot interaction)
        responses = gather_missing_info(questions, data['job_id'])
        data.update(responses)

    # Finalize the prompt with the available data
    final_prompt = prompt_template.format(**data)

    # Call the OpenAI API to generate the job description
    generated_description = call_openai_api(final_prompt)
    
    return generated_description

def load_prompt():
    prompt_path = "services/prompts/generate_job_description.txt"
    with open(prompt_path, 'r') as file:
        return file.read()

def check_missing_fields(data):
    required_fields = [
        'title', 'company_name', 'location', 'type', 
        'time_commitment', 'description', 'requirements'
    ]
    missing = {field: None for field in required_fields if not data.get(field)}
    return missing

def generate_questions_for_missing_fields(missing_fields):
    questions = {}
    if 'title' in missing_fields:
        questions['title'] = "Please provide the title of the job position."
    if 'company_name' in missing_fields:
        questions['company_name'] = "Please provide the company or organization's name."
    if 'location' in missing_fields:
        questions['location'] = "Please provide the job location."
    if 'type' in missing_fields:
        questions['type'] = "Is this job remote, hybrid, or onsite?"
    if 'time_commitment' in missing_fields:
        questions['time_commitment'] = "Is this a full-time, part-time, or contract position?"
    if 'description' in missing_fields:
        questions['description'] = "Please provide a detailed description of the roles and responsibilities."
    if 'requirements' in missing_fields:
        questions['requirements'] = "Please list the key skills and qualifications required for the job."
    if 'estimated_pay' in missing_fields:
        questions['estimated_pay'] = "Please provide the estimated pay range for this position."
    if 'job_level' in missing_fields:
        questions['job_level'] = "Please specify the job level (e.g., entry-level, junior, middle, senior)."
    # Add more questions for each missing field as needed
    return questions

def gather_missing_info(questions, job_id):
    responses = {}
    for field, question in questions.items():
        # Here, instead of a placeholder, you would integrate with your chatbot or API to get this data.
        # This could involve sending an HTTP request to a service that handles gathering recruiter inputs.
        response = get_info_from_chatbot_or_api(job_id, field, question)
        responses[field] = response
    return responses

def fill_missing_fields_with_defaults(data):
    # Provide default values for any missing fields
    defaults = {
        'job_level': "Not specified",
        'estimated_pay': "Not specified"
    }
    for field, default_value in defaults.items():
        if not data.get(field):
            data[field] = default_value
    return data

def call_openai_api(prompt):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI assistant that helps generate comprehensive and compelling job descriptions based on the provided data.",
                    "role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_info_from_chatbot_or_api(job_id, field, question):
    # Example: Call an API that interacts with the recruiter to get missing information
    # This is a placeholder for your actual implementation

    api_url = os.getenv('INFO_GATHERING_API_URL')  # Ensure you have this environment variable set
    headers = {'Authorization': f"Bearer {os.getenv('API_TOKEN')}"}

    payload = {
        'job_id': job_id,
        'field': field,
        'question': question
    }

    response = requests.post(api_url, json=payload, headers=headers)
    response_data = response.json()

    return response_data.get('answer')


# def get_info_from_chatbot_or_api(job_id, field, question):
#     # Mock interaction for local testing
#     mock_responses = {
#         'title': "Software Engineer",
#         'company_name': "TechCorp Inc.",
#         'location': "San Francisco, CA",
#         'type': "remote",
#         'time_commitment': "full-time",
#         'description': "Develop and maintain web applications.",
#         'requirements': "Experience with Python and JavaScript.",
#         'estimated_pay': "$100,000 - $120,000",
#         'job_level': "Junior"
#     }
#     print(f"Question: {question}")
#     return mock_responses.get(field, "Default Answer")
