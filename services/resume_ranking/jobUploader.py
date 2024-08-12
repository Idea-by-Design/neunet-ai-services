import os
import yaml
import json
from common.database.cosmos.db_setup import setup_database
from common.database.cosmos.db_operations import upsert_jobDetails
from services.resume_parser.parser.openai_resume_parser import parse_resume_json
from services.resume_parser.parser.doc_parser import parse_doc
from services.resume_parser.parser.pdf_parser import parse_pdf

def main(file_path):
    
    # Load database configuration
    with open("config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    # Setup database connection
    _, container = setup_database(
        config['database']['cosmos_db_uri'],
        config['database']['cosmos_db_key'],
        config['database']['cosmos_db_name'],
        config['database']['job_description_container_name']
    )
    
    # Upsert resume data to the database
    try:
        upsert_jobDetails(container, file_path)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # file_path = 'test string for job description'
    import json
    x =  '{ "id":"23456", "jd":"test jd"}'
    file_path = json.loads(x)
    main(file_path)
