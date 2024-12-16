from azure.cosmos import CosmosClient, exceptions
from common.utils.config_utils import load_config
from datetime import datetime
import ast


# Load configuration
config = load_config()
COSMOS_ENDPOINT = config['database']['cosmos_db_uri']
COSMOS_KEY = config['database']['cosmos_db_key']
DATABASE_NAME = config['database']['cosmos_db_name']

# Container names
RESUMES_CONTAINER_NAME = config['database']['resumes_container_name']
GITHUB_CONTAINER_NAME = config['database']['github_container_name']
RANKING_CONTAINER_NAME = config['database']['ranking_container_name']
JOBS_CONTAINER_NAME = config['database']['job_description_container_name']
APPLICATIONS_CONTAINER_NAME = config['database']['application_container_name']
JOB_DESCRIPTION_QUESTIONNAIRE_CONTAINER_NAME = config['database']['job_description_questionnaire_container_name']
# RECRUITMENT_PROCESS_CONTAINER_NAME = config['database']['recruitment_process_container_name']

# Initialize Cosmos DB client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
resumes_container = database.get_container_client(RESUMES_CONTAINER_NAME)
github_container = database.get_container_client(GITHUB_CONTAINER_NAME)
ranking_container = database.get_container_client(RANKING_CONTAINER_NAME)
jobs_container = database.get_container_client(JOBS_CONTAINER_NAME)
applications_container = database.get_container_client(APPLICATIONS_CONTAINER_NAME)
job_description_questionnaire_container = database.get_container_client(JOB_DESCRIPTION_QUESTIONNAIRE_CONTAINER_NAME)
# recruitment_process_container = database.get_container_client(RECRUITMENT_PROCESS_CONTAINER_NAME)

def upsert_resume(container, resume_data):
    try:
        resumes_container.upsert_item(resume_data)
        print(f"Resume data upserted successfully for {resume_data['email']}!")
    except Exception as e:
        print(f"An error occurred while upserting resume: {e}")

def upsert_jobDetails(jobData):
    try:
        jobs_container.upsert_item(jobData)
        print(f"Job data upserted successfully!")
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

# def store_application(application_data):
#     try:
#         application_container.upsert_item(body=application_data)
#         print(f"Application data stored successfully for {application_data['id']}")
#     except exceptions.CosmosHttpResponseError as e:
#         print(f"Failed to store application data: {e}")

# def fetch_application(application_id):
#     try:
#         query = f"SELECT * FROM c WHERE c.id = '{application_id}'"
#         results = list(application_container.query_items(query=query, enable_cross_partition_query=True))
#         return results[0] if results else None
#     except Exception as e:
#         print(f"An error occurred while fetching application: {e}")
#         return None
    
def store_job_questionnaire(questionnaire_data):
    try:
        print(f"Storing questionnaire data for {questionnaire_data['job_id']}")
        job_description_questionnaire_container.upsert_item(body=questionnaire_data)
        print(f"Questionnaire data stored successfully for {questionnaire_data['job_id']}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to store Questionnaire data: {e}")
        
def fetch_job_description_questionnaire(job_id):
    try:
        # Treat job_id as a number (without quotes)
        query = f"SELECT * FROM c WHERE c.job_id = {job_id}"
        results = list(job_description_questionnaire_container.query_items(query=query, enable_cross_partition_query=True))
        
        if results:
            print(f"Job description questionnaire fetched successfully for job ID: {job_id}")
            return results[0]
        else:
            print(f"No job description questionnaire found for job ID: {job_id}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching job description questionnaire: {e}")
        return None

    
    
def fetch_resume_with_email(email):
    try:
        # Correcting the query to fetch the first matching document for the provided email
        query = """
        SELECT * 
        FROM c
        WHERE IS_DEFINED(c.email) AND c.email = @email
        """
        parameters = [
            {"name": "@email", "value": email}
        ]

        print(f"Executing query to fetch resume for email: {email}...")

        # Execute the query and retrieve only the first matching result
        candidates = resumes_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )
        
        # Return the first matched document, or None if no match
        for candidate in candidates:
            print("Resume fetched successfully!")
            return candidate  # Return the first matched document
        
        print("No resume found for the given email.")
        return None
    
    except Exception as e:
        print(f"An error occurred while fetching resume: {e}")
        return None
    
    # db_operations.py

def fetch_application_by_job_id(job_id):
    try:
        query = """
        SELECT * 
        FROM c
        WHERE c.job_id = @job_id
        """
        parameters = [{"name": "@job_id", "value": job_id}]
        results = list(applications_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        if results:
            print(f"Application found for job ID: {job_id}")
            return results[0]
        else:
            print(f"No application found for job ID: {job_id}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching application: {e}")
        return None



def create_application_for_job_id(job_id, job_questionnaire_id):
    try:
        # Create a new document with job_id, job_questionnaire_id, and unique_id
        new_application = {
            "job_id": job_id,
            "job_questionnaire_id": job_questionnaire_id,
            "id": f"{job_id}_{job_questionnaire_id}",  # Create a unique identifier
            # Add any additional fields as required
        }

        # Insert the new document into the Cosmos DB container
        applications_container.create_item(body=new_application)

        print(f"New application created for job ID: {job_id}")
        return new_application

    except Exception as e:
        print(f"An error occurred while creating application: {e}")
        return None


def save_ranking_data_to_cosmos_db(ranking_data, candidate_email, ranking, conversation, resume):
    try:
        # Check if "candidates" key exists in ranking_data
        if "candidates" not in ranking_data:
            ranking_data["candidates"] = []

        # Check if candidate already exists based only on email
        for candidate in ranking_data["candidates"]:
            if candidate["email"].lower() == candidate_email.lower():  # Case-insensitive email comparison
                # Return early indicating the candidate has already applied
                return f"Error: The candidate with email {candidate_email} has already applied."

        # If candidate doesn't exist, add a new entry
        new_candidate = {
            "email": candidate_email,
            "ranking": ranking,
            "conversation": conversation,
            "resume": resume,
            "application_status": "Applied"
        }
        ranking_data["candidates"].append(new_candidate)

        # Update existing document
        if "id" in ranking_data:
            applications_container.replace_item(item=ranking_data["id"], body=ranking_data)
            print(f"Ranking data successfully updated in Cosmos DB for {candidate_email}.")
            return f"Success: The candidate with email {candidate_email} has been added."
        else:
            return "Error: No 'id' found in ranking_data, cannot update the document."
    except Exception as e:
        print(f"An error occurred while saving ranking data: {e}")
        return f"An error occurred: {e}"




import ast

def fetch_top_k_candidates_by_count(job_id, top_k=10):
    try:
        # Define the query to fetch job_title and the candidates (resume, email, ranking)
        query = """
        SELECT c.job_title, candidate.resume, candidate.email, candidate.ranking
        FROM c
        JOIN candidate IN c.candidates
        WHERE c.job_id = @job_id
        """
        parameters = [
            {"name": "@job_id", "value": job_id}
        ]

        # Query the applications container
        results = list(applications_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        # If results exist, format them into the required output
        if results:
            print(f"Application found for job ID: {job_id}")

            # Extract job_title from the first result (same for all candidates in the document)
            job_title = results[0]["job_title"]

            candidate_list = []
            for result in results:
                email = result["email"]
                ranking = result["ranking"]

                # Safely parse the resume to extract the name
                resume = result.get("resume", "{}")
                try:
                    parsed_resume = ast.literal_eval(resume)
                    name = parsed_resume.get('name', 'N/A')
                except (ValueError, SyntaxError):
                    name = "Invalid JSON"

                candidate_list.append({"name": name, "email": email, "ranking": ranking})

            # Sort candidates by ranking in descending order
            sorted_candidates = sorted(candidate_list, key=lambda x: x['ranking'], reverse=True)

            # Return the top k candidates
            top_candidates = sorted_candidates[:top_k]
            return {"job_title": job_title, "top_candidates": top_candidates}

        else:
            print(f"No application found for job ID: {job_id}")
            return None

    except Exception as e:
        print(f"An error occurred while fetching application: {e}")
        return None


import ast

def fetch_top_k_candidates_by_percentage(job_id, percentage=10):
    try:
        # Define the query to fetch job_title and the candidates (resume, email, ranking)
        query = """
        SELECT c.job_title, candidate.resume, candidate.email, candidate.ranking
        FROM c
        JOIN candidate IN c.candidates
        WHERE c.job_id = @job_id
        """
        parameters = [
            {"name": "@job_id", "value": job_id}
        ]

        # Query the applications container
        results = list(applications_container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        # If results exist, format them into the required output
        if results:
            print(f"Application found for job ID: {job_id}")

            # Extract job_title from the first result (same for all candidates in the document)
            job_title = results[0]["job_title"]

            candidate_list = []
            for result in results:
                email = result["email"]
                ranking = result["ranking"]

                # Safely parse the resume to extract the name
                resume = result.get("resume", "{}")
                try:
                    parsed_resume = ast.literal_eval(resume)
                    name = parsed_resume.get('name', 'N/A')
                except (ValueError, SyntaxError):
                    name = "Invalid JSON"

                candidate_list.append({"name": name, "email": email, "ranking": ranking})

            # Sort candidates by ranking in descending order
            sorted_candidates = sorted(candidate_list, key=lambda x: x['ranking'], reverse=True)

            # Calculate the top percentage number of candidates to return
            top_count = max(1, int(len(sorted_candidates) * (percentage / 100)))

            # Return the job title and top percentage candidates
            top_candidates = sorted_candidates[:top_count]
            return {"job_title": job_title, "top_candidates": top_candidates}

        else:
            print(f"No application found for job ID: {job_id}")
            return None

    except Exception as e:
        print(f"An error occurred while fetching application: {e}")
        return None


def update_application_status(job_id, candidate_email, new_status):
    valid_statuses = [
        "Applied",
        "Application Under Review",
        "Interview Invite Sent",
        "Interview Scheduled",
        "Interview Feedback Under Review",
        "Offer Extended",
        "Rejected",
        "Withdrawn"
    ]

    try:
        # Fetch the job document from Cosmos DB using the job_id
        job_document = applications_container.read_item(item=str(job_id), partition_key=str(job_id))
        
        # Check if "candidates" key exists
        if "candidates" not in job_document:
            return f"Error: No candidates found for job ID {job_id}."

        # Search for the candidate by email
        for candidate in job_document["candidates"]:
            if candidate["email"].lower() == candidate_email.lower():  # Case-insensitive comparison
                # Update the application status
                if new_status in valid_statuses:
                    candidate["application_status"] = new_status
                    # Update the document in Cosmos DB
                    applications_container.replace_item(item=job_document["id"], body=job_document)
                    return f"Success: Application status for {candidate_email} updated to '{new_status}'."
                else:
                    candidate["application_status"] = "Unknown"
                    # Update the document in Cosmos DB
                    applications_container.replace_item(item=job_document["id"], body=job_document)
                    return f"Error: Invalid status '{new_status}' provided. Status set to 'Unknown'."

        return f"Error: Candidate with email {candidate_email} not found for job ID {job_id}."
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"
