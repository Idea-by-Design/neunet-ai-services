import os
import json
from dotenv import load_dotenv
from services.resume_ranking.resume_ranker.multiagent_resume_ranker import initiate_chat
from common.database.cosmos.db_operations import fetch_job_description, fetch_job_description_questionnaire, fetch_resume_with_email
import json
import datetime

# Load environment variables
load_dotenv()

def rank_resume_for_candidate(job_description_id, candidate_email):
    # Call DB to fetch Job Description
    job_description = fetch_job_description(job_description_id)
    
    # Call DB to fetch Job Description Questionnaire
    job_description_questionnaire = fetch_job_description_questionnaire(job_description_id)
    questionnaire_id = job_description_questionnaire['id']
    questions = job_description_questionnaire['questionnaire']
    
    # Fetch resume for the candidate
    resume = fetch_resume_with_email(candidate_email)
    
    print(f"Starting resume ranking test for {candidate_email}...")
    result = initiate_chat(job_description_id, questionnaire_id, resume, job_description, candidate_email, questions)
    print(f"Ranking for {candidate_email} completed successfully.")
    
    return result

def main():
    
    # ## Test 1 Blockchain developer
    
    # # List of email IDs
    # email_list = [
    #     "garvitjain1857@gmail.com",
    #     "minhthangminh1992@gmail.com",
    #     "chrisgodev@gmail.com",
    #     "jlucusjobs@gmail.com",
    #     "jay3183@gmail.com",
    #     "arjunnambiar.nk@gmail.com",
    #     "anthonytilotta303@gmail.com",
    #     "ravidharnia151@gmail.com",
    #     "codyrowirth@yahoo.com",
    #     "suhailroyeen@gmail.com",
    #     "ayanpatel_98@yahoo.com",
    #     "scott815@gmail.com",
    #     "ycheng345@gatech.edu",
    #     "rdfx2@proton.me"
    # ]
    
    # # Job description ID (can be parameterized as needed)
    # job_description_id = 123457
    
    
    ## Test 2 Devops engineer 
        
    # List of email IDs
    email_list = [
    # Bad
    "tbenkhelifa3@gmail.com",
    "johnjjarthur@gmail.com",
    "sirus1257@gmail.com",
    "hannagropen@gmail.com",
    "williamchen5667@gmail.com",
    "davidsilveira.3.djs@gmail.com",
    "johnadaggs@gmail.com",
    "JustinR.WrightEng@gmail.com",

    # Good
    "victorbnelson@gmail.com",
    "Alamfareed51@gmail.com",
    "Pranavumesh1415@gmail.com",
    "ramkashy@buffalo.edu",
    "edekikume@gmail.com",
    "ravi09devops@gmail.com",
    "SherazHu1@gmail.com",
    "navyav0406@gmail.com"
]

    # Job description ID (can be parameterized as needed)
    job_description_id = 123458
    
    # Loop through the email list and rank each resume
    for email in email_list:
        result = rank_resume_for_candidate(job_description_id, email)
        # You can save or print the result as needed
        print(f"Result for {email}: {result}")

if __name__ == "__main__":
    main()
