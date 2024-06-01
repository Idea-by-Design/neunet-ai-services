from azure.cosmos import CosmosClient
import yaml

def load_config():
    with open("config/config.yaml", 'r') as file:
        return yaml.safe_load(file)

def test_cosmos_db_connection(uri, key):
    try:
        # Initialize the Cosmos client
        client = CosmosClient(uri, key)
        
        # List databases to test the connection
        databases = list(client.list_databases())
        
        print("Connection to Cosmos DB was successful!")
        print("Databases:", databases)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    config = load_config()
    test_cosmos_db_connection(
        config['database']['cosmos_db_uri'],
        config['database']['cosmos_db_key']
    )
