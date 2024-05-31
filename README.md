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
