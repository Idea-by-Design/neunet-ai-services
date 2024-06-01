from sqlalchemy import create_engine
import yaml
from azure.storage.blob import BlobServiceClient

def test_database_connection():
    with open("config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    connection_string = config['database']['connection_string']
    engine = create_engine(connection_string)
    
    try:
        with engine.connect() as connection:
            print("Connection to the database was successful!")
    except Exception as e:
        print(f"An error occurred: {e}")

def test_storage_account_connection():
    with open("config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    storage_account_name = config['azure']['storage_account_name']
    storage_account_key = config['azure']['storage_account_key']
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        print("Connection to the storage account was successful!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_database_connection()
    test_storage_account_connection()
