import azure.functions as func
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from common.database.cosmos.db_operations import (
    fetch_job_posts, fetch_candidates, schedule_meeting, 
    generate_job_post, reach_out_to_candidate
)
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Initialize the Conversation Analysis Client
    credential = AzureKeyCredential("<your_language_service_key>")
    client = ConversationAnalysisClient("<your_language_service_endpoint>", credential)

    # Get the user's message
    message = req.params.get('message')
    
    # Analyze the intent of the message
    result = client.analyze_conversation(
        task={
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "text": message,
                    "id": "1",
                    "participantId": "user"
                },
                "isLoggingEnabled": False
            },
            "parameters": {
                "projectName": "<your_luis_project_name>",
                "deploymentName": "<your_luis_deployment_name>",
                "verbose": True
            }
        }
    )

    # Extract the top intent
    top_intent = result["result"]["prediction"]["topIntent"]

    # Handle different intents
    if top_intent == "FetchCandidates":
        job_id = extract_job_id(message)
        candidates = fetch_candidates(job_id)
        return func.HttpResponse(f"Top candidates for job {job_id}: {candidates}")
    elif top_intent == "GenerateJobPost":
        job_details = extract_job_details(message)
        job_post = generate_job_post(job_details)
        return func.HttpResponse(f"Generated job post: {job_post}")
    elif top_intent == "ReachOutToCandidate":
        candidate_id = extract_candidate_id(message)
        job_id = extract_job_id(message)
        result = reach_out_to_candidate(candidate_id, job_id)
        return func.HttpResponse(f"Reached out to candidate {candidate_id}: {result}")
    elif top_intent == "ScheduleMeeting":
        candidate_id = extract_candidate_id(message)
        recruiter_id = extract_recruiter_id(message)
        meeting_details = extract_meeting_details(message)
        result = schedule_meeting(candidate_id, recruiter_id, meeting_details)
        return func.HttpResponse(f"Scheduled meeting: {result}")
    else:
        return func.HttpResponse("I'm sorry, I didn't understand that request.")

def extract_job_id(message):
    match = re.search(r'job[_\s]?id[:\s]?(\w+)', message, re.IGNORECASE)
    return match.group(1) if match else None

def extract_job_details(message):
    # Assuming job details are provided in a structured format
    details = {}
    patterns = {
        'title': r'title[:\s]?(.+?)(?:\n|$)',
        'company': r'company[:\s]?(.+?)(?:\n|$)',
        'location': r'location[:\s]?(.+?)(?:\n|$)',
        'description': r'description[:\s]?(.+?)(?:\n|$)',
        'requirements': r'requirements[:\s]?(.+?)(?:\n|$)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, message, re.IGNORECASE | re.DOTALL)
        if match:
            details[key] = match.group(1).strip()
    return details

def extract_candidate_id(message):
    match = re.search(r'candidate[_\s]?id[:\s]?(\w+)', message, re.IGNORECASE)
    return match.group(1) if match else None

def extract_recruiter_id(message):
    match = re.search(r'recruiter[_\s]?id[:\s]?(\w+)', message, re.IGNORECASE)
    return match.group(1) if match else None

def extract_meeting_details(message):
    details = {}
    patterns = {
        'start_time': r'start[_\s]?time[:\s]?(.+?)(?:\n|$)',
        'end_time': r'end[_\s]?time[:\s]?(.+?)(?:\n|$)',
        'location': r'meeting[_\s]?location[:\s]?(.+?)(?:\n|$)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()
    return details