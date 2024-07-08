# neunet-ai-services


This repository contains multiple AI services. Each service is modular and organized in a separate directory under the `services/` directory.

## Setup

1. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Configure settings**:
   - Edit the `config/config.yaml` file with your database and Azure settings.

3. **Install the ODBC Driver for SQL Server:**
    - You need the Microsoft ODBC Driver for SQL Server installed on your machine. You can download it from Microsoft's official website.


## Repository Structure

- `common/` - Contains shared modules and utilities.
- `services/` - Contains directories for individual services.
  - `resume_parser/` - Resume parsing service.
- `scripts/` - Deployment and local run scripts.
- `docs/` - Documentation for each service.


## Database

resumes
github
ranking
jobs
recruitment_process

I believe these five containers should be sufficient for most recruitment system needs. Here's why:

The "resumes" container covers candidate information and parsed resume data.
The "github" container handles GitHub analysis for candidates.
The "ranking" container manages candidate rankings for specific jobs.
The "jobs" container stores all job posting information.
The "recruitment_process" container tracks the status and stages of recruitment for each candidate-job pair.

These containers cover the main entities and processes in a typical recruitment system. However, there are a couple of considerations:

Interviews: The interview scheduling and feedback could be incorporated into the "recruitment_process" container. Each stage in the recruitment process could include interview details if applicable.
User/Recruiter Information: If you need to store information about recruiters or system users, you might consider adding this to the "recruitment_process" container (by including a recruiter_id field) or creating a separate "users" container if you need more detailed user management.

schema suggested is in updated_schema.json