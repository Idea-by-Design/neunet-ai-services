import os
from services.resume_ranking.job_description_questionnaire.jd_questionnaire_generator import generate_questionnaire, save_questionnaire


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
    
    
def main():
    # Mock API Key (Replace this with a real API key or retrieve it from environment variables)
    api_key = os.getenv("OPENAI_API_KEY")

    # Sample Job Description
    job_description_path = r"services\resume_ranking\test_data\sample_files\sample_job_description.txt"
    job_description = read_file_to_string(job_description_path)
    # Output folder and filename
    output_folder = r"services\resume_ranking\test_data\job_questionnaire_results"  # Ensure 'output' folder is created in the current script's directory
    output_filename = "job_questionnaire.txt"  

    # Generate questionnaire using the job description
    print("Generating questionnaire...")
    questionnaire = generate_questionnaire(job_description)

    # Save the questionnaire to a JSON file
    print("Saving questionnaire to JSON...")
    output_path = save_questionnaire(questionnaire, output_folder, output_filename)

    # Confirm completion
    print(f"Questionnaire saved at: {output_path}")

if __name__ == '__main__':
    main()
    # way to run: python -m services.resume_ranking.tests.test_jd_question_maker 
