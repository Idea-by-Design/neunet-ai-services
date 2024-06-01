import yaml
import json
from common.database.cosmos.db_setup import setup_database
from common.database.cosmos.db_operations import upsert_resume
from services.resume_parser.openai_resume_parser import parse_resume

def main(file_path):
    # Parse resume using OpenAI API
    extracted_info = parse_resume(file_path)
    
    # Print extracted information
    print("##############################\n", extracted_info, "\n##############################\n")

    # Convert JSON string to dictionary
    resume_data = json.loads(extracted_info)

    # Load database configuration
    with open("config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    # Setup database connection
    _, container = setup_database(
        config['database']['cosmos_db_uri'],
        config['database']['cosmos_db_key'],
        config['database']['cosmos_db_name'],
        config['database']['container_name']
    )
    
    # Upsert resume data to the database
    upsert_resume(container, resume_data)

if __name__ == "__main__":
    file_path = 'F:\\Job-Search\\VedikaSrivastava_Resume_May2024.pdf'
    main(file_path)
