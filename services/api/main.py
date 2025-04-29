from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import random
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.database.cosmos import db_operations

app = FastAPI(title="Neunet Recruitment API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neunet.io", "https://www.neunet.io", "http://localhost:5173", "http://localhost:3000"],  # Production and development origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobQuestionnaire(BaseModel):
    questions: List[str]

class JobDescription(BaseModel):
    title: str
    location: str
    job_type: str
    description: str
    requirements: str
    responsibilities: str
    salary_range: str
    benefits: Optional[str] = None
    company_culture: Optional[str] = None
    interview_process: Optional[str] = None
    growth_opportunities: Optional[str] = None
    tech_stack: Optional[str] = None
    questionnaire: Optional[JobQuestionnaire] = None
    job_id: str = Field(default_factory=lambda: str(random.randint(100000, 999999)))
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @validator('job_id')
    def validate_job_id(cls, v):
        if not (len(v) == 6 and v.isdigit()):
            raise ValueError('job_id must be a 6-digit number')
        return v

class CandidateRanking(BaseModel):
    job_id: str
    candidate_email: str
    ranking: float
    conversation: str
    resume: dict

class CandidateApplication(BaseModel):
    name: str
    email: str
    resume: str
    cover_letter: Optional[str] = None
    ranking: float = Field(default=0.85)  # For testing, we'll set a default ranking

class JobDescriptionRequest(BaseModel):
    title: str = None
    company_name: str = None
    location: str = None
    type: str = None
    time_commitment: str = None
    description: str = None
    requirements: str = None
    job_id: str = None

# Job Description Endpoints
@app.get("/jobs/")
async def list_jobs():
    try:
        print("Fetching all jobs...")  # Debug log
        jobs = db_operations.fetch_all_jobs()
        print(f"Fetched jobs: {jobs}")  # Debug log
        return jobs if jobs else []
    except Exception as e:
        print(f"Error fetching jobs: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/")
async def create_job(job: JobDescription):
    try:
        # Generate a new 6-digit job ID if not provided
        if not job.job_id:
            job.job_id = str(random.randint(100000, 999999))
        
        job_data = job.dict()
        job_data["id"] = job_data["job_id"]  # Ensure id is set for Cosmos DB
        
        print("Creating job with data:", job_data)  # Debug log
        
        # Store in Cosmos DB
        db_operations.upsert_jobDetails(job_data)
        return {"message": "Job created successfully", "job_id": job.job_id}
    except Exception as e:
        print(f"Error creating job: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        job = db_operations.fetch_job_description(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}/questionnaire")
async def get_job_questionnaire(job_id: str):
    try:
        job = db_operations.fetch_job_description(job_id)
        if not job or not job.get("questionnaire"):
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        return job["questionnaire"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Candidate Endpoints
@app.get("/jobs/{job_id}/candidates")
async def get_job_candidates(job_id: str, top_k: int = 10):
    try:
        candidates = db_operations.fetch_top_k_candidates_by_count(job_id, top_k)
        if not candidates:
            return []
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/{job_id}/candidates/{candidate_email}/status")
async def update_candidate_status(job_id: str, candidate_email: str, status: str):
    try:
        db_operations.update_application_status(job_id, candidate_email, status)
        return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/candidates/{email}/resume")
async def get_candidate_resume(email: str):
    try:
        resume = db_operations.fetch_resume_with_email(email)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Application Endpoints
@app.get("/applications/{job_id}")
async def get_job_applications(job_id: str):
    try:
        applications = db_operations.fetch_application_by_job_id(job_id)
        if not applications:
            return []
        return applications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: str, application: CandidateApplication):
    try:
        print(f"Received application for job {job_id}: {application}")  # Debug log
        
        # Create application data
        application_data = {
            "id": f"{job_id}_{application.email}",  # Composite key for job_id and email
            "job_id": job_id,
            "name": application.name,
            "email": application.email,
            "resume": application.resume,
            "cover_letter": application.cover_letter,
            "ranking": application.ranking,
            "status": "applied",
            "applied_at": datetime.utcnow().isoformat(),
            "type": "candidate"  # Identify this as a candidate record
        }
        
        print(f"Submitting application: {application_data}")  # Debug log
        
        # Store in Cosmos DB
        result = db_operations.upsert_candidate(application_data)
        print(f"Application submitted: {result}")  # Debug log
        
        return {"message": "Application submitted successfully"}
    except Exception as e:
        print(f"Error submitting application: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/candidates/{job_id}")
async def get_candidates_for_job(job_id: str):
    candidates = db_operations.fetch_top_k_candidates_by_count(job_id)
    return {"count": len(candidates), "candidates": candidates}

@app.post("/api/generate-job-description")
def generate_job_description(request: JobDescriptionRequest):
    from services.ai_job_description.generate_description import generate_description
    import json
    try:
        data = request.dict()
        generated = generate_description(data)
        # Clean and robustly parse the AI's response as JSON, even if double-encoded
        cleaned = generated.strip()
        if cleaned.lower().startswith('json'):
            cleaned = cleaned.split('\n', 1)[-1]
        cleaned = cleaned.strip('`')
        # Try to parse multiple times if necessary
        for _ in range(3):
            try:
                cleaned = json.loads(cleaned)
            except Exception:
                break
            if isinstance(cleaned, dict):
                return cleaned
        # If parsing fails, return as a string
        return {"job_description": generated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
