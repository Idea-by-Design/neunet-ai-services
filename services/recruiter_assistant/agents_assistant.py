import autogen
import os
from dotenv import load_dotenv
from typing import List, Dict
import json
from datetime import datetime, timedelta

# Import functions from other services
from common.database.cosmos.db_operations import (
    fetch_job_description,
    fetch_candidates_with_github_links,
    fetch_recruitment_processes,
    fetch_candidate_rankings,
    store_candidate_ranking,
    fetch_github_analysis,
    update_recruitment_process
)

# Load environment variables
load_dotenv()

# Fetch API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Configuration for AI models
config_list = [{"model": "gpt-3.5-turbo", "api_key": api_key}]

def is_termination_msg(message):
    return message.get("content") and "TERMINATE" in message["content"]

# Function declarations
def get_top_candidates(job_id: str, percentile: int = 10) -> str:
    # Fetch job description
    job = fetch_job_description(job_id)
    if not job:
        return f"Error: Job {job_id} not found"

    # Fetch existing rankings for this job
    rankings = fetch_candidate_rankings(job_id)
    
    # Determine which candidates need ranking
    candidates = fetch_candidates_with_github_links()
    candidates_to_rank = [
        c for c in candidates 
        if c['email'] not in rankings or 
        rankings[c['email']]['ranked_at'] < datetime.now() - timedelta(days=7)
    ]

    # Rank candidates who need ranking
    for candidate in candidates_to_rank:
        resume = candidate
        github_analysis = fetch_github_analysis(candidate['email'])
        ranking = calculate_ranking(resume, github_analysis, job)
        store_candidate_ranking(job_id, candidate['email'], ranking)
        rankings[candidate['email']] = {
            'ranking': ranking,
            'ranked_at': datetime.now()
        }

    # Sort all candidates by their rankings
    ranked_candidates = sorted(
        rankings.items(), 
        key=lambda x: x[1]['ranking'], 
        reverse=True
    )

    # Select top candidates
    top_count = max(1, int(len(ranked_candidates) * percentile / 100))
    top_candidates = [candidate[0] for candidate in ranked_candidates[:top_count]]

    return f"Top {percentile}% candidates for job {job_id}: {', '.join(top_candidates)}"

def calculate_ranking(resume: Dict, github_analysis: Dict, job: Dict) -> float:
    # Implement your ranking algorithm here
    # This is a placeholder implementation
    skill_match = len(set(resume.get('skills', [])) & set(job.get('required_skills', []))) / len(job.get('required_skills', []))
    experience_match = min(resume.get('experience', 0) / job.get('min_experience', 1), 1)
    github_score = github_analysis.get('overall_score', 0) if github_analysis else 0
    
    return (skill_match * 0.4 + experience_match * 0.3 + github_score * 0.3) * 10

def generate_job_post(job_details: Dict[str, any]) -> str:
    # This function remains largely the same, but now it would use the 'jobs' container
    title = job_details.get('title', 'Unnamed Position')
    skills = ', '.join(job_details.get('required_skills', []))
    experience = job_details.get('min_experience', 'Not specified')
    
    job_post = f"""
    Job Title: {title}
    
    We are seeking a talented individual to join our team as a {title}. 
    The ideal candidate will have the following skills: {skills}.
    
    Required Experience: {experience} years
    
    If you are passionate about technology and want to work in a dynamic environment, 
    we encourage you to apply!
    """
    
    return f"Job post generated:\n{job_post}"

def reach_out_to_candidate(candidate_email: str, job_id: str) -> str:
    candidate = fetch_candidates_with_github_links(candidate_email)
    job = fetch_job_description(job_id)
    
    if not candidate:
        return f"Error: Candidate {candidate_email} not found"
    if not job:
        return f"Error: Job {job_id} not found"

    message = f"""
    Dear {candidate['name']},

    I hope this message finds you well. We have an exciting opportunity for a {job['title']} position 
    that I believe would be a great fit for your skills and experience.

    Would you be interested in discussing this opportunity further?

    Best regards,
    Recruiting Team
    """

    # Update the recruitment process
    update_recruitment_process(job_id, candidate_email, 'contacted')

    return f"Reached out to candidate {candidate_email} for job {job_id}. Message sent:\n{message}"

def schedule_interview(candidate_email: str, job_id: str, date_time: str) -> str:
    candidate = fetch_candidates_with_github_links(candidate_email)
    if not candidate:
        return f"Error: Candidate {candidate_email} not found"

    try:
        meeting_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Error: Invalid date-time format. Please use YYYY-MM-DD HH:MM"

    # Update the recruitment process
    update_recruitment_process(job_id, candidate_email, 'interview_scheduled', {
        'interview_time': meeting_time.isoformat()
    })

    return f"Interview scheduled for {candidate['name']} on {date_time} for job {job_id}"

def track_recruitment_pipeline(job_id: str) -> str:
    # Fetch all recruitment processes for the given job
    processes = fetch_recruitment_processes(job_id)
    
    pipeline_status = {
        'applied': [],
        'contacted': [],
        'interview_scheduled': [],
        'offer_extended': [],
        'hired': []
    }

    for process in processes:
        status = process.get('status', 'applied')
        pipeline_status[status].append(process['candidate_email'])

    report = "Recruitment Pipeline Status:\n"
    for status, candidates in pipeline_status.items():
        report += f"{status.capitalize()}: {len(candidates)} candidates\n"

    return report

# Define agents
user_proxy = autogen.UserProxyAgent(
    name="recruiter_proxy",
    system_message="You're the recruiter seeking assistance.",
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    function_map={
        "get_top_candidates": get_top_candidates,
        "generate_job_post": generate_job_post,
        "reach_out_to_candidate": reach_out_to_candidate,
        "schedule_interview": schedule_interview,
        "track_recruitment_pipeline": track_recruitment_pipeline
    },
    code_execution_config={"use_docker": False}
)

candidate_sourcer = autogen.AssistantAgent(
    name="candidate_sourcer",
    system_message="""You are a specialist in sourcing top candidates. Your primary tasks are:
    1. Identifying top percentile candidates for job posts
    2. Analyzing candidate profiles and matching them to job requirements
    Use the get_top_candidates function to perform your tasks.""",
    llm_config={"config_list": config_list}
)

job_poster = autogen.AssistantAgent(
    name="job_poster",
    system_message="""You are an expert in creating compelling job postings. Your main responsibility is:
    1. Generating attractive and informative job posts
    Use the generate_job_post function to create job listings.""",
    llm_config={"config_list": config_list}
)

outreach_specialist = autogen.AssistantAgent(
    name="outreach_specialist",
    system_message="""You specialize in candidate outreach. Your key tasks include:
    1. Reaching out to top candidates on behalf of recruiters
    2. Crafting personalized messages to engage potential candidates
    Use the reach_out_to_candidate function for your outreach efforts.""",
    llm_config={"config_list": config_list}
)

scheduler = autogen.AssistantAgent(
    name="scheduler",
    system_message="""You are responsible for managing schedules and setting up interviews. Your main task is:
    1. Scheduling interviews with candidates and recruiters
    Use the schedule_interview function to arrange interviews.""",
    llm_config={"config_list": config_list}
)

pipeline_tracker = autogen.AssistantAgent(
    name="pipeline_tracker",
    system_message="""You are in charge of monitoring the recruitment pipeline. Your primary responsibility is:
    1. Tracking candidates in the pipeline and providing status updates
    Use the track_recruitment_pipeline function to monitor the pipeline and report on its status.""",
    llm_config={"config_list": config_list}
)

# Set up group chat
group_chat = autogen.GroupChat(
    agents=[user_proxy, candidate_sourcer, job_poster, outreach_specialist, scheduler, pipeline_tracker],
    messages=[]
)

group_chat_manager = autogen.GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": config_list}
)

def initiate_chat(recruiter_request: str, job_id: str) -> str:
    chat_result = user_proxy.initiate_chat(
        group_chat_manager,
        message=f"""Process the following recruiter request:

        Recruiter's Request: '{recruiter_request}'
        Job ID (if applicable): '{job_id}'

        Each specialist should handle their respective tasks:
        1. Candidate Sourcer: Identify top percentile candidates for the job post.
        2. Job Poster: Generate a job post if needed.
        3. Outreach Specialist: Reach out to top candidates.
        4. Scheduler: Schedule interviews with candidates if required.
        5. Pipeline Tracker: Track candidates in the pipeline and provide status updates.

        Collaborate as needed to fulfill the recruiter's request efficiently.
        """
    )
    return json.dumps(chat_result, indent=2)

if __name__ == "__main__":
    recruiter_request = "Find top candidates for Job1 and schedule interviews"
    job_id = "job-12345"
    result = initiate_chat(recruiter_request, job_id)
    print(result)