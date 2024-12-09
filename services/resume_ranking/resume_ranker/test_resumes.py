import os
import json
import logging
import time
from dotenv import load_dotenv
from services.resume_ranking.resume_ranker.multiagent_resume_ranker import initiate_chat
from common.database.cosmos.db_operations import fetch_job_description, fetch_job_description_questionnaire, fetch_resume_with_email

# Set up logging
log_file_path = os.path.join(os.getcwd(), 'resume_ranking.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# # Load environment variables
# load_dotenv()

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
    # Record start time
    start_time = time.time()

    # List of email IDs
    email_list = [
        # Good resumes:
         "vedikas3012@gmail.com"
        # "ganeshthanu17@gmail.com",
        # "khushilmodi17@gmail.com",
        # "suryasaith@gmail.com",
        # "saitulasi1729@gmail.com",
        # "abireads01@outlook.com",
        # "amit.bh@gatech.edu",
        # "pinki22shiv2016@gmail.com",

        # # Bad resumes:
        # "Benjamin.Rohrs@gmail.com",
        # "minal.patilr30@gmail.com",
        # "srilalithamv18@gmail.com",
        # "rishikotadiya1711@gmail.com",
        # "guillem.cobos93@gmail.com",
        # "khan27@jhu.edu"
    ]

    # Job description ID (can be parameterized as needed)
    job_description_id = 123486
    
    # Loop through the email list and rank each resume
    for email in email_list:
        logging.info(f"Processing resume for {email}")
        result = rank_resume_for_candidate(job_description_id, email)
        if result:
            logging.info(f"Result for {email}: {result}")
        else:
            logging.error(f"Failed to rank resume for {email}")

    # Record end time
    end_time = time.time()

    # Calculate total time taken
    total_time = end_time - start_time

    # Log and print the total time taken
    logging.info(f"Total time taken for resume ranking: {total_time:.2f} seconds.")
    print(f"Total time taken for resume ranking: {total_time:.2f} seconds.")   # Total time taken for resume ranking: 130.07 seconds.

if __name__ == "__main__":
    main()

