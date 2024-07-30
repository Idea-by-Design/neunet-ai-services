from azure.cosmos import CosmosClient, exceptions
from common.utils.config_utils import load_config
from datetime import datetime

# Load configuration
config = load_config()
COSMOS_ENDPOINT = config['database']['cosmos_db_uri']
COSMOS_KEY = config['database']['cosmos_db_key']
DATABASE_NAME = config['database']['cosmos_db_name']

# Container names
RESUMES_CONTAINER_NAME = config['database']['resumes_container_name']
GITHUB_CONTAINER_NAME = config['database']['github_container_name']
RANKING_CONTAINER_NAME = config['database']['ranking_container_name']
# JOBS_CONTAINER_NAME = config['database']['jobs_container_name']
APPLICATION_CONTAINER_NAME = config['database']['application_container_name']
# RECRUITMENT_PROCESS_CONTAINER_NAME = config['database']['recruitment_process_container_name']

# Initialize Cosmos DB client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
resumes_container = database.get_container_client(RESUMES_CONTAINER_NAME)
github_container = database.get_container_client(GITHUB_CONTAINER_NAME)
ranking_container = database.get_container_client(RANKING_CONTAINER_NAME)
# jobs_container = database.get_container_client(JOBS_CONTAINER_NAME)
application_container = database.get_container_client(APPLICATION_CONTAINER_NAME)
# recruitment_process_container = database.get_container_client(RECRUITMENT_PROCESS_CONTAINER_NAME)

def upsert_resume(container, resume_data):
    try:
        resumes_container.upsert_item(resume_data)
        print(f"Resume data upserted successfully for {resume_data['email']}!")
    except Exception as e:
        print(f"An error occurred while upserting resume: {e}")

def fetch_candidates_with_github_links():
    try:
        query = """
        SELECT c.email, c.links.gitHub AS github
        FROM c
        WHERE IS_DEFINED(c.links.gitHub)
        """
        print("Executing query to fetch candidates with GitHub links...")
        candidates = list(resumes_container.query_items(query=query, enable_cross_partition_query=True))
        print(f"Fetched {len(candidates)} candidates.")
        for candidate in candidates:
            print(candidate)
        return candidates
    except Exception as e:
        print(f"An error occurred while fetching candidates: {e}")
        return []

def store_github_analysis(analysis_data):
    try:
        print(f"Storing analysis data for {analysis_data['email']}")
        github_container.upsert_item(body=analysis_data)
        print(f"GitHub analysis data stored successfully for {analysis_data['email']}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to store GitHub analysis data: {e}")

def fetch_github_analysis(email):
    try:
        query = f"SELECT * FROM c WHERE c.email = '{email}'"
        results = list(github_container.query_items(query=query, enable_cross_partition_query=True))
        return results[0] if results else None
    except Exception as e:
        print(f"An error occurred while fetching GitHub analysis: {e}")
        return None

def fetch_job_description(job_id):
    try:
        query = f"SELECT * FROM c WHERE c.id = '{job_id}'"
        results = list(jobs_container.query_items(query=query, enable_cross_partition_query=True))
        if results:
            print(f"Job description fetched successfully for job ID: {job_id}")
            return results[0]
        else:
            print(f"No job description found for job ID: {job_id}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching job description: {e}")
        return None

def store_candidate_ranking(job_id, candidate_email, ranking):
    try:
        ranking_data = {
            "id": f"{job_id}_{candidate_email}",
            "job_id": job_id,
            "candidate_email": candidate_email,
            "ranking": ranking,
            "ranked_at": datetime.utcnow().isoformat()
        }
        ranking_container.upsert_item(ranking_data)
        print(f"Ranking stored successfully for job {job_id} and candidate {candidate_email}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to store ranking: {e}")

def fetch_candidate_rankings(job_id):
    try:
        query = f"SELECT c.candidate_email, c.ranking, c.ranked_at FROM c WHERE c.job_id = '{job_id}'"
        rankings = list(ranking_container.query_items(query=query, enable_cross_partition_query=True))
        return {r['candidate_email']: {'ranking': r['ranking'], 'ranked_at': r['ranked_at']} for r in rankings}
    except Exception as e:
        print(f"An error occurred while fetching candidate rankings: {e}")
        return {}
    
    
def update_recruitment_process(job_id, candidate_email, status, additional_info=None):
    try:
        process_id = f"{job_id}_{candidate_email}"
        process_data = {
            "id": process_id,
            "job_id": job_id,
            "candidate_email": candidate_email,
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        if additional_info:
            process_data.update(additional_info)
        recruitment_process_container.upsert_item(process_data)
        print(f"Recruitment process updated for job {job_id} and candidate {candidate_email}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to update recruitment process: {e}")

def fetch_recruitment_processes(job_id):
    try:
        query = f"SELECT * FROM c WHERE c.job_id = '{job_id}'"
        processes = list(recruitment_process_container.query_items(query=query, enable_cross_partition_query=True))
        return processes
    except Exception as e:
        print(f"An error occurred while fetching recruitment processes: {e}")
        return []

def store_application(application_data):
    try:
        application_container.upsert_item(body=application_data)
        print(f"Application data stored successfully for {application_data['id']}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to store application data: {e}")

def fetch_application(application_id):
    try:
        query = f"SELECT * FROM c WHERE c.id = '{application_id}'"
        results = list(application_container.query_items(query=query, enable_cross_partition_query=True))
        return results[0] if results else None
    except Exception as e:
        print(f"An error occurred while fetching application: {e}")
        return None