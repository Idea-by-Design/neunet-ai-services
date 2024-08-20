import os
import json
from dotenv import load_dotenv
from ..agent_call import initiate_chat
# Load environment variables
load_dotenv()

# Ensure you have set the OPENAI_API_KEY in your .env file
if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError("Please set the OPENAI_API_KEY environment variable in your .env file")

# Mock data
mock_resume = """
John Doe
Email: john.doe@example.com
Phone: (123) 456-7890

Summary:
Experienced software engineer with 5 years of experience in web development and cloud technologies.

Skills:
- Python, JavaScript, React, Node.js
- AWS, Docker, Kubernetes
- Agile methodologies, CI/CD

Experience:
Software Engineer, TechCorp (2018-2023)
- Developed and maintained web applications using React and Node.js
- Implemented microservices architecture using Docker and Kubernetes
- Optimized application performance, resulting in 30% faster load times

Education:
Bachelor of Science in Computer Science, University of Technology (2014-2018)
"""

mock_job_description = """
Senior Software Engineer

We are seeking a Senior Software Engineer to join our dynamic team. The ideal candidate will have:

- 5+ years of experience in software development
- Strong proficiency in Python and JavaScript
- Experience with React and Node.js
- Familiarity with cloud technologies (AWS, Azure, or GCP)
- Knowledge of containerization and orchestration (Docker, Kubernetes)
- Experience with Agile methodologies and CI/CD practices

Responsibilities:
- Design and implement scalable web applications
- Collaborate with cross-functional teams to define and implement new features
- Optimize application performance and ensure high availability
- Mentor junior developers and contribute to code reviews

If you are passionate about technology and want to work on cutting-edge projects, we'd love to hear from you!
"""

mock_candidate_email = "john.doe@example.com"

def print_json_content():
    try:
        with open("ranking_data.json", "r") as file:
            data = json.load(file)
            print("Contents of ranking_data.json:")
            print(json.dumps(data, indent=2))
    except FileNotFoundError:
        print("ranking_data.json file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from ranking_data.json.")
        
        
def test_resume_ranking():
    print("Starting resume ranking test...")
    result = initiate_chat(mock_resume, mock_job_description, mock_candidate_email)
    print("Test completed. Check the ranking_data.json file for results.")
    print("\nPrinting contents of ranking_data.json:")
    print_json_content()
    return result

if __name__ == "__main__":
    test_resume_ranking()