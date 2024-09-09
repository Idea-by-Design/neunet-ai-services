import os
import json
from dotenv import load_dotenv
from services.resume_ranking.resume_ranker.multiagent_resume_ranker import initiate_chat
# Load environment variables
load_dotenv()

# Ensure you have set the OPENAI_API_KEY in your .env file
if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError("Please set the OPENAI_API_KEY environment variable in your .env file")


# Function to load a file as a string
def read_file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except IOError:
        print(f"Error: There was an issue reading the file at {file_path}.")
        return None

def print_json_content():
    try:
        with open(r"services\resume_ranking\test_data\ranking_results\ranking_data.json", "r") as file:
            data = json.load(file)
            print("Contents of ranking_data.json:")
            print(json.dumps(data, indent=2))
    except FileNotFoundError:
        print(r"services\resume_ranking\test_data\ranking_results\ranking_data.json file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from ranking_data.json.")
        
        
def main():
    
    # Sample data 
    job_description_path = r"services\resume_ranking\test_data\sample_files\sample_job_description.txt"
    job_description = f"""{read_file_to_string(job_description_path)}"""
    
    # resume_path = r"services\resume_ranking\test_data\sample_files\sample_resume_1.txt"
    # resume = f"""{read_file_to_string(resume_path)}"""
    # candidate_email= "john.doe@example.com"
    
    resume_path = r"services\resume_ranking\test_data\sample_files\sample_resume_2.txt"
    resume = read_file_to_string(resume_path)
    candidate_email= "jane.smith@example.com"

    questionnaire_path = r"services\resume_ranking\test_data\job_questionnaire_results\job_questionnaire.txt"
    questionnaire = f"""{read_file_to_string(questionnaire_path)}"""
    print("contents of questionnaire: ", questionnaire)
    
    print("Starting resume ranking test...")
    result = initiate_chat(resume, job_description, candidate_email, questionnaire)
    print("Test completed. Check the ranking_data.json file for results.")
    print("\nPrinting contents of ranking_data.json:")
    print_json_content()
    return result

if __name__ == "__main__":
    main()