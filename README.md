# Neunet AI Services

A powerful backend service that handles job postings, candidate applications, and AI-powered candidate matching for the Neunet platform.

## Tech Stack

### Backend Framework
- FastAPI (v0.104.1) - Modern, fast web framework for building APIs with Python
- Uvicorn (v0.24.0) - Lightning-fast ASGI server implementation

### Database
- Azure Cosmos DB (v4.5.1) - Globally distributed, multi-model database service
- Multiple containers for different data types:
  - Job descriptions
  - Applications
  - Resumes
  - GitHub analysis
  - Rankings
  - Questionnaires

### Authentication & Security
- Python-Jose (v3.3.0) - JavaScript Object Signing and Encryption implementation
- Passlib (v1.7.4) - Password hashing library
- BCrypt (v4.0.1) - Password hashing

### Data Validation
- Pydantic (v2.4.2) - Data validation using Python type annotations

## Project Structure

```
neunet-ai-services/
├── common/
│   ├── database/
│   │   └── cosmos/         # Cosmos DB operations
│   └── utils/             # Utility functions
├── config/
│   └── config.yaml        # Configuration settings
├── services/
│   └── api/
│       └── main.py        # FastAPI application
├── scripts/
│   └── run_api.sh        # Server startup script
├── requirements.txt      # Python dependencies
└── README.md
```

## Features

1. Job Management
   - Create and manage job postings
   - Store job descriptions and requirements
   - Handle job questionnaires

2. Application Processing
   - Process candidate applications
   - Store resumes and cover letters
   - Track application status

3. Candidate Analysis
   - GitHub profile analysis
   - Resume parsing
   - Candidate ranking

## API Endpoints

### Jobs
- `POST /jobs/` - Create a new job posting
- `GET /jobs/{job_id}` - Get job details
- `GET /jobs/` - List all jobs

### Applications
- `POST /jobs/{job_id}/apply` - Submit job application
- `GET /jobs/{job_id}/applications` - Get job applications
- `GET /debug/candidates/{job_id}` - Get candidates for a job

## Deployment

The API is deployed to Azure App Service and can be accessed at https://neunet-api.azurewebsites.net.

## Deployment Status

Deployed to Azure App Service at: https://neunet-api.azurewebsites.net

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure Azure Cosmos DB settings in `config/config.yaml`
4. Run the server:
   ```bash
   ./scripts/run_api.sh
   ```

## Configuration

The application uses a YAML configuration file (`config/config.yaml`) for:
- Database connection settings
- Container names
- API configurations

## Development

1. Start the development server:
   ```bash
   cd services/api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. The API will be available at `http://localhost:8000`

## Security

- Implements secure password hashing with BCrypt
- Uses JWT for authentication
- Supports CORS for frontend integration