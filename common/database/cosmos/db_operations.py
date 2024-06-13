from azure.cosmos import CosmosClient, exceptions
from common.utils.config_utils import load_config

# Load configuration
config = load_config()
COSMOS_ENDPOINT = config['database']['cosmos_db_uri']
COSMOS_KEY = config['database']['cosmos_db_key']
DATABASE_NAME = config['database']['cosmos_db_name']
RESUMES_CONTAINER_NAME = config['database']['container_name']
GITHUB_ANALYSIS_CONTAINER_NAME = config['database']['github_container_name']

# Initialize Cosmos DB client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
resumes_container = database.get_container_client(RESUMES_CONTAINER_NAME)
github_analysis_container = database.get_container_client(GITHUB_ANALYSIS_CONTAINER_NAME)


def upsert_resume(container, resume_data):
    try:
        container.upsert_item(resume_data)
        print("Data upserted successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


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
        github_analysis_container.create_item(body=analysis_data)
        print("Analysis data stored successfully.")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to store data: {e}")