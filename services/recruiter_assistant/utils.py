from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
from common.database.cosmos.db_operations import fetch_candidates, fetch_job_details

import openai
from common.database.cosmos.db_operations import store_job_post,fetch_candidate_details, fetch_job_details, store_outreach_message
from common.email.sender import send_email
from azure.identity import DefaultAzureCredential
from msgraph.core import GraphClient
from common.database.cosmos.db_operations import fetch_candidate_details, fetch_recruiter_details, store_meeting_details

openai.api_key = "<your_openai_api_key>"

def identify_top_candidates(job_id, percentile=10):
    # Fetch all candidates who applied for the job
    candidates = fetch_candidates(job_id)
    
    # Extract features from candidates
    features = extract_features(candidates, job_id)
    
    # Normalize features
    scaler = StandardScaler()
    normalized_features = scaler.fit_transform(features)
    
    # Apply PCA for dimensionality reduction
    pca = PCA(n_components=5)  # Adjust the number of components as needed
    pca_features = pca.fit_transform(normalized_features)
    
    # Calculate distances from the ideal candidate (assumed to be at the origin after PCA)
    distances = np.linalg.norm(pca_features, axis=1)
    
    # Calculate the percentile threshold
    threshold = np.percentile(distances, percentile)
    
    # Select top candidates
    top_candidates = [candidate for candidate, distance in zip(candidates, distances) if distance <= threshold]
    
    return top_candidates

def extract_features(candidates, job_id):
    job_details = fetch_job_details(job_id)
    required_skills = set(job_details.get('required_skills', []))
    preferred_skills = set(job_details.get('preferred_skills', []))
    
    features = []
    for candidate in candidates:
        candidate_skills = set(candidate.get('skills', []))
        
        feature_vector = [
            len(required_skills & candidate_skills) / len(required_skills) if required_skills else 0,
            len(preferred_skills & candidate_skills) / len(preferred_skills) if preferred_skills else 0,
            candidate.get('years_of_experience', 0) / job_details.get('required_experience', 1),
            1 if candidate.get('education_level') >= job_details.get('required_education_level', 0) else 0,
            candidate.get('relevant_projects', 0) / 5  # Assuming a scale of 0-5 for relevant projects
        ]
        features.append(feature_vector)
    
    return np.array(features)


def generate_job_post(job_details):
    prompt = f"""Generate a professional job post for the following position:

    Title: {job_details.get('title', 'N/A')}
    Company: {job_details.get('company', 'N/A')}
    Location: {job_details.get('location', 'N/A')}
    Description: {job_details.get('description', 'N/A')}
    Requirements: {job_details.get('requirements', 'N/A')}

    Please format the job post with appropriate sections and bullet points."""

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    generated_post = response.choices[0].text.strip()
    
    # Store the generated job post
    job_post_id = store_job_post(job_details, generated_post)
    
    return {"job_post_id": job_post_id, "content": generated_post}


def reach_out_to_candidate(candidate_id, job_id):
    # Fetch candidate and job details
    candidate = fetch_candidate_details(candidate_id)
    job = fetch_job_details(job_id)
    
    # Generate personalized message
    message = generate_outreach_message(candidate, job)
    
    # Send message
    result = send_email(candidate['email'], "Exciting Job Opportunity", message)
    
    # Store the outreach message
    store_outreach_message(candidate_id, job_id, message)
    
    return result

def generate_outreach_message(candidate, job):
    prompt = f"""Generate a personalized outreach message to a candidate with the following details:

    Candidate Name: {candidate['name']}
    Candidate Skills: {', '.join(candidate['skills'])}
    Candidate Experience: {candidate['years_of_experience']} years

    Job Title: {job['title']}
    Company: {job['company']}
    Job Description: {job['description']}

    The message should be friendly, professional, and highlight why the candidate would be a good fit for the position."""

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    return response.choices[0].text.strip()


def schedule_meeting(candidate_id, recruiter_id, meeting_details):
    # Fetch candidate and recruiter details
    candidate = fetch_candidate_details(candidate_id)
    recruiter = fetch_recruiter_details(recruiter_id)
    
    # Create Graph client
    credential = DefaultAzureCredential()
    graph_client = GraphClient(credential)
    
    # Create meeting request
    meeting_request = {
        "subject": f"Interview with {candidate['name']}",
        "body": {
            "contentType": "HTML",
            "content": f"Interview for the position of {meeting_details.get('position', 'N/A')}"
        },
        "start": {
            "dateTime": meeting_details['start_time'],
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": meeting_details['end_time'],
            "timeZone": "UTC"
        },
        "location": {
            "displayName": meeting_details.get('location', 'Online')
        },
        "attendees": [
            {
                "emailAddress": {
                    "address": candidate['email'],
                    "name": candidate['name']
                },
                "type": "required"
            },
            {
                "emailAddress": {
                    "address": recruiter['email'],
                    "name": recruiter['name']
                },
                "type": "required"
            }
        ]
    }
    
    # Send meeting request
    response = graph_client.post('/me/events', json=meeting_request)
    meeting_data = response.json()
    
    # Store meeting details
    store_meeting_details(candidate_id, recruiter_id, meeting_data)
    
    return meeting_data