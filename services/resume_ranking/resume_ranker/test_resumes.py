import os
import json
from dotenv import load_dotenv
from services.resume_ranking.resume_ranker.multiagent_resume_ranker import initiate_chat
from common.database.cosmos.db_operations import fetch_job_description, fetch_job_description_questionnaire, fetch_resume_with_email
import logging

# Set up logging
log_file_path = os.path.join(os.getcwd(), 'resume_ranking.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

def rank_resume_for_candidate(job_description_id, candidate_email):
    try:
        # Call DB to fetch Job Description
        job_description = fetch_job_description(job_description_id)
        
        # Call DB to fetch Job Description Questionnaire
        job_description_questionnaire = fetch_job_description_questionnaire(job_description_id)
        questionnaire_id = job_description_questionnaire['id']
        questions = job_description_questionnaire['questionnaire']
        
        # Fetch resume for the candidate
        resume = fetch_resume_with_email(candidate_email)
        
        logging.info(f"Starting resume ranking test for {candidate_email} with job description ID {job_description_id}.")
        result = initiate_chat(job_description_id, questionnaire_id, resume, job_description, candidate_email, questions)
        logging.info(f"Ranking for {candidate_email} completed successfully.")
        
        return result

    except Exception as e:
        logging.error(f"An error occurred for candidate {candidate_email}: {e}")
        return None

def main():
    # List of email IDs
    email_list = [
        "garvitjain1857@gmail.com",
        "minhthangminh1992@gmail.com",
        "chrisgodev@gmail.com",
        "jlucusjobs@gmail.com",
        "jay3183@gmail.com",
        "arjunnambiar.nk@gmail.com",
        "anthonytilotta303@gmail.com",
        "ravidharnia151@gmail.com",
        "codyrowirth@yahoo.com",
        "suhailroyeen@gmail.com",
        "ayanpatel_98@yahoo.com",
        "scott815@gmail.com",
        "ycheng345@gatech.edu",
        "rdfx2@proton.me"
    ]
    
    # Job description ID (can be parameterized as needed)
    job_description_id = 123457
    
    # Loop through the email list and rank each resume
    for email in email_list:
        logging.info(f"Processing resume for {email}")
        result = rank_resume_for_candidate(job_description_id, email)
        if result:
            logging.info(f"Result for {email}: {result}")
        else:
            logging.error(f"Failed to rank resume for {email}")

if __name__ == "__main__":
    main()
