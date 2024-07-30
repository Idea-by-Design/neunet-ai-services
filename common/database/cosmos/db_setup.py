from azure.cosmos import CosmosClient, PartitionKey
from common.utils.config_utils import load_config

def setup_database():
    config = load_config()
    client = CosmosClient(config['database']['cosmos_db_uri'], config['database']['cosmos_db_key'])
    database = client.create_database_if_not_exists(id=config['database']['cosmos_db_name'])
    
    # Create containers
    database.create_container_if_not_exists(
        id=config['database']['resumes_container_name'],
        partition_key=PartitionKey(path="/email"),
        offer_throughput=400
    )
    database.create_container_if_not_exists(
        id=config['database']['github_container_name'],
        partition_key=PartitionKey(path="/email"),
        offer_throughput=400
    )
    database.create_container_if_not_exists(
        id=config['database']['ranking_container_name'],
        partition_key=PartitionKey(path="/job_id"),
        offer_throughput=400
    )
    database.create_container_if_not_exists(
        id=config['database']['jobs_container_name'],
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )
    database.create_container_if_not_exists(
        id=config['database']['application_container_name'],
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )
    database.create_container_if_not_exists(
        id=config['database']['recruitment_process_container_name'],
        partition_key=PartitionKey(path="/job_id"),
        offer_throughput=400
    )
    
    print(f"Database '{config['database']['cosmos_db_name']}' and containers set up successfully.")
    return client, database

if __name__ == "__main__":
    setup_database()