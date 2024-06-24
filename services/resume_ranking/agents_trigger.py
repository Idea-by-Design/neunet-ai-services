import logging
import azure.functions as func
from services.resume_ranking import initiate_chat
from common.database.cosmos.db_operations import store_matching_result, fetch_job_description


# Assuming their is application db with data of resume and job description id  and unique id for each application
def main(applications: func.DocumentList) -> str:
    logging.info("Processing applications for resume and job description analysis")
    
    for application in applications:
        application_id = application.get('id')
        resume_data = application.get('resumeData')
        
        job_id = application.get('jobId')
        
        logging.info(f"Processing application {application_id} for job {job_id}")
        
        # Fetch the related job description
        job_description = fetch_job_description(job_id)
        
        # # Fetch the resume data
        # resume_id = resume_data.get('resumeid')
        # resume_data = fetch_resume_data(resume_data)
        
        if resume_data and job_description:
            # Perform the analysis
            result = initiate_chat(resume_data, job_description, resume_data.get('email'))
            
            # Store the result
            store_matching_result(application_id, resume_data.get('id'), job_id, result)
        else:
            logging.warning(f"Could not process application {application_id}. Missing resume data or job description.")

    return "Application processing completed"


''' sample application data schema we can store resume data here or just resume id here and fetch from resume db
    
     like below        
           
        # # Fetch the resume data
        # resume_id = resume_data.get('resumeid')
        # resume_data = fetch_resume_data(resume_data)
        
 schema for application data assumed is
{
  "id": "application_12345",
  "resumeData": {
    "id": "resume_67890",
    "email": "candidate@example.com",
    "name": "John Doe",
    "skills": ["Python", "Azure", "Machine Learning"],
    "experience": [
      {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "duration": "2018-2021"
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science in Computer Science",
        "institution": "University of Technology",
        "year": 2018
      }
    ]
  },
  "jobId": "job_54321",
  "applicationDate": "2023-06-15T14:30:00Z",
  "status": "submitted"
} '''