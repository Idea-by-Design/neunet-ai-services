import autogen
import os
from common.database.cosmos.db_operations import fetch_top_k_candidates_by_count, fetch_top_k_candidates_by_percentage, update_application_status, execute_sql_query
from services.chatbot.functions import send_email
from dotenv import load_dotenv

# Load environment variables from .env file in the project directory
load_dotenv(dotenv_path=".env")


# # Fetch the API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")


# # Configuration for AI models
# config_list = [{"model": "gpt-4o", "api_key": api_key}]


# Configuration for Azure OpenAI models
config_list = [{"model": os.getenv("deployment_name"),  
                            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                            "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
                            "api_type": os.getenv("api_type"),  
                            "api_version": os.getenv("api_version")}]

# Define the User Proxy Agent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=50,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"use_docker": False}
)

# Define the Executor Agent to run functions
executor_agent_prompt = '''
This agent executes all functions for the group. 
It receives function requests from other agents and runs them with the provided arguments. 
MAKE SURE TO GENERATE CORRECT ARGUMENTS BEFORE RUNNING THE FUNCTION.

'''
executor_agent = autogen.AssistantAgent(
    name="function_executor_agent",
    system_message=executor_agent_prompt,
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "fetch_top_k_candidates_by_percentage",
                "description": "Fetches the top percentage of candidates (email and ranking only) for a given job ID. ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "number",
                            "description": "The job ID for which to fetch the application data."
                        },
                        "percentage": {
                            "type": "number",
                            "description": "The percentage of top candidates to fetch, defaults to 10%."
                        }
                    },
                    "required": ["job_id"]
                }
            },
            {
                "name": "fetch_top_k_candidates_by_count",
                "description": "Fetches the top count of candidates (email and ranking only) for a given job ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "number",
                            "description": "The job ID for which to fetch the application data."
                        },
                        "percentage": {
                            "type": "number",
                            "description": "The count of top candidates to fetch, defaults to 10."
                        }
                    },
                    "required": ["job_id"]
                }
            },
            {
                "name": "send_email",
                "description": "Sends an email to a list of recipients.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_addresses": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of email addresses to send the email to."
                        },
                        "subject": {
                            "type": "string",
                            "description": "The subject of the email."
                        },
                        "body_plain": {
                            "type": "string",
                            "description": "The plain text content of the email."
                        }
                    },
                    "required": ["to_addresses", "subject", "body_plain"]
                }
            },
            {
                "name": "update_application_status",
                "description": "Updates the status of application for given job application and candidate email id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "number",
                            "description": "The job ID for which to update the application status."
                        },
                        "candidate_email": {
                            "type": "string",
                            "description": "The email of the candidate whose status is to be updated."
                        },
                        "new_status": {
                            "type": "string",
                            "description": "The new status to be set for the candidate."
                        }
                    },
                    "required": ["job_id", "candidate_email", "new_status"]
                }
            },
            {
                "name": "execute_sql_query",
                "description": "Executes the given SQL query generated by the sql_query_generator_agent. This function can be used if there is no other function that solved user request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute."
                        }
                    }
                }
            }

        ]
    },
)



    

# Register the functions with the executor agent
executor_agent.register_function(
    function_map={
        "fetch_top_k_candidates_by_percentage": fetch_top_k_candidates_by_percentage,
        "fetch_top_k_candidates_by_count": fetch_top_k_candidates_by_count,
        "send_email": send_email,
        "update_application_status": update_application_status,
        "execute_sql_query": execute_sql_query
    }
)




# Define the Fetcher Agent
fetcher_agent_prompt = '''
You are a Candidate Fetching Agent responsible for retrieving the top candidates for a given job ID.

Task:
Understand the request:
- If the user requests candidates by count, call the executor to run fetch_top_k_candidates_by_count.
- If the request is by percentage, call the executor to run fetch_top_k_candidates_by_percentage.
- For non-standard requests (e.g., total number of candidates):
    Improvise by using available functions creatively. For instance, if the user wants the total number of candidates, run the fetch_top_k_candidates_by_percentage function with 100% and count the results.
- If no function can fulfill the request, then use the pre-defined functions as reference to create a new function. and ask the executer agent to execute and return the results.
Return the results:
Output the top candidates' email IDs and rankings after fetching.
Ensure the result is properly sorted and concise.
'''
fetcher_agent = autogen.AssistantAgent(
    name="top_candidate_fetcher",
    system_message=fetcher_agent_prompt,
    llm_config={
        "config_list": config_list,
    },
)


# Email Service Agent
email_agent_prompt = """
You are an Email Service Agent, responsible for managing and executing all email-related tasks with precision and efficiency.

[Task]: You will handle user requests for the following service:

[Service 1]: Sending interview invitation emails to top candidates or specific email addresses.

This service requires two function calls:
1. send_email
2. update_application_status

Process:
1. Understand the request:
   - Use the results from the Candidate Fetching Agent to obtain email addresses and rankings.

2. Draft the email:
   - Compose a professional and engaging email content.
   - Include essential information: appropriate subject; content with candidate name, job title.
   - Incorporate the Calendly link: "https://calendly.com/hemant-singh-ideaxdesign/30min?email={candidate_email}&job_id={job_id}"


3. Prepare for sending:
   - Compile the email arguments (recipients, subject, content).
   - Display the draft email (subject and content) to the user for final confirmation.
   - If the user requests changes, make necessary adjustments and seek confirmation again.

4. Send the email: 
   - Once confirmed, ask the executor to run the send_email function with the prepared arguments.

5. Update application status:
   - After successful email sending, automatically update the application status for each recipient.
   - Use the update_application_status function with arguments: job_id, candidate_email, and new_status ("Interview Invite Sent").

6. Confirmation and reporting:
   - Provide a summary to the user, including the number of emails sent and status updates made.

"""

email_agent = autogen.AssistantAgent(
    name="email_service_agent",
    system_message=email_agent_prompt,
    llm_config={
        "config_list": config_list,
    },
)


# Define job description creator agent
job_desc_creator_agent_prompt = """
You are a job description generator agent who takes input from user and makes a job description out of the given information. 
And if there is limited information then you can ask user for more information.

Please generate a comprehensive job description using the information provided below. 
The final output should be a JSON object that includes all relevant details structured appropriately.


Instructions:
1. Structure: The final job description should be returned as a JSON object with the following keys:
  - job_title
  - company_name
  - about
    - more about the company
  - location
  - estimated_pay_range
  - job_type
  - time_commitment
  - job_level
  - about_the_role
  - key_responsibilities (as a list of bullet points)
    - List the key responsibilities for this role based on the information provided above.
    - Make sure to include tasks that will help the candidate understand what a typical day might look like in this role.
  - qualifications (as a list of bullet points)
    - Detail the qualifications necessary for this role.
    - Include education, experience, and specific skills or certifications required.
  - skills_and_competencies (as a list of bullet points)
    - List out the core skills and competencies needed to succeed in this role.
    - Highlight any software, tools, or methodologies that are essential.
  - benefits (as a list of bullet points)
    - Outline the benefits provided by the company (e.g., health insurance, 401(k), remote work options, etc.).
    - Mention any unique perks that the company offers.

2. Content Guidelines:
  - About the Role: Use description to craft a compelling overview of the role.
  - Key Responsibilities: Extract and list the main responsibilities from description to help candidates understand daily tasks.
  - Qualifications: Detail the necessary qualifications using requirements, including education, experience, and certifications.
  - Skills and Competencies: Highlight core skills and any essential software, tools, or methodologies from requirements.
  - Benefits: Use benefits to list the benefits and any unique company perks.


3. Style:
  - Ensure the language is engaging and clear.
  - Tailor the description to attract suitable candidates.
  - Use professional and inclusive language.

4. Missing Information:
  - If any field is missing or empty, you can omit it from the JSON or use a general placeholder like "To be discussed".


5. Example JSON Structure:
    ```JSON
    {
      "job_title": "title",
      "company_name": "company_name",
      "location": "location",
      "estimated_pay_range": "estimated_pay",
      "job_type": "type",
      "time_commitment": "time_commitment",
      "job_level": "job_level",
      "about_the_role": "description",
      "key_responsibilities": [
        "Responsibility 1",
        "Responsibility 2",
        "..."
      ],
      "qualifications": [
        "Qualification 1",
        "Qualification 2",
        "..."
      ],
      "skills_and_competencies": [
        "Skill 1",
        "Skill 2",
        "..."
      ],
      "benefits": [
        "Benefit 1",
        "Benefit 2",
        "..."
      ]
    }
    ```

Final Output:
Please generate the job description as a JSON object following the instructions above.
Ensure that the generated job description is engaging, clear, and tailored to attract the right candidates for this position. If certain information is not provided, please note that and generate a general placeholder or request additional details from the recruiter.
"""


job_desc_creator_agent = autogen.AssistantAgent(
    name="job_description_creator_agent",
    system_message=job_desc_creator_agent_prompt,
    llm_config={
        "config_list": config_list,
    },
)

# Define the SQL Query Generator Agent's prompt
sql_query_generator_prompt = """
You are an advanced SQL Query Generator for the 'applications' container in Cosmos DB.
Your job is to convert a natural language request into a valid Cosmos DB SQL query.

## Container Schema Overview

Each document in the 'applications' container typically has the following structure:
{
  "id":         <string>,  // Unique identifier for the document (often matches job_id as a string)
  "job_id":     <number>,  // The numeric job ID
  "job_title":  <string>,  // Title or name of the job
  "candidates": [
    {
      "resume":            <string or object>,  // The candidate's resume data (often stored as a JSON string)
      "email":             <string>,            // Candidate's email address
      "ranking":           <number>,            // Candidate's ranking or score
      "application_status":<string>             // Current status of the candidate's application
    },
    ...
  ],
  // Potentially other fields...
}

## Important Notes

1. **Chain-of-thought reasoning**: You should reason internally step by step to derive the correct SQL query. However, **do not reveal** your chain-of-thought in the final output. The user should only see the final SQL query string.

2. **Query Requirements**:
   - Cosmos DB SQL syntax.
   - The container alias is typically `c`.
   - When querying array fields (like `candidates`), we often do `JOIN candidate IN c.candidates`.
   - Pay attention to data types (e.g., `job_id` is numeric, so do not quote it in your WHERE clause).
   - For string comparisons, you can use functions like `LOWER()` if you need case-insensitive matching.

3. **Existing Query Examples**:
   - **Fetching Top K Candidates by Count**:
     ```
     SELECT c.job_title, candidate.resume, candidate.email, candidate.ranking
     FROM c
     JOIN candidate IN c.candidates
     WHERE c.job_id = @job_id
     ```
     This query retrieves candidates (resume, email, ranking) for a given job ID.
   
   - **Fetching Top K Candidates by Percentage**:
     ```
     SELECT c.job_title, candidate.resume, candidate.email, candidate.ranking
     FROM c
     JOIN candidate IN c.candidates
     WHERE c.job_id = @job_id
     ```
     Similar to the above, but the business logic afterwards calculates the top percentage.

   - **Updating Application Status** (not strictly SQL, but demonstrates how data is structured):
     - We read the item by `job_id` and partition key:
       ```
       job_document = applications_container.read_item(item=str(job_id), partition_key=str(job_id))
       ```
       Then update fields in the `candidates` array and replace the item.

4. **Guidelines**:
   - Output **only** the final SQL query string, with no extra text or commentary.
   - If a user query references the `candidates` array, use a `JOIN candidate IN c.candidates` approach as needed.
   - If a user wants to filter by `job_id`, remember it’s numeric (e.g., `WHERE c.job_id = 10001`).
   - If a user wants to filter by candidate’s name or email, be mindful that these are stored inside each element of `candidates`.
   - If a user’s query is ambiguous, you can either ask clarifying questions or make a reasonable assumption (but only output the final SQL in your response).

## Examples

1. **Simple Name & Job ID**  
   **Input**: "Show details of candidate with name Hemant Kumar Singh for job id 10001"  
   **Output**: SELECT * FROM c WHERE c.job_id = 10001 AND LOWER(c.name) = 'hemant kumar singh'

   _(If the user wants data from the `candidates` array, you might need `JOIN candidate IN c.candidates`.)_

2. **Retrieve Candidate Data**  
   **Input**: "Retrieve the application data for candidate John Doe for job id 20002"  
   **Output**: SELECT * FROM c JOIN candidate IN c.candidates WHERE c.job_id = 20002 AND LOWER(candidate.email) = 'john.doe@example.com'

3. **Using Existing Patterns**  
   If the user says "Fetch top K candidates by ranking for job 10003," you might produce a query like:
   SELECT c.job_title, candidate.resume, candidate.email, candidate.ranking FROM c JOIN candidate IN c.candidates WHERE c.job_id = 10003 ORDER BY candidate.ranking DESC

(Though the actual top-K logic might happen in code after retrieving results.)

Remember: **Do not show your chain-of-thought**. Provide only the final SQL query as the answer so the executer agent can  use it as parameter in execute_sql_query function.


"""

# Create the SQL Query Generator Agent
sql_query_generator_agent = autogen.AssistantAgent(
    name="sql_query_generator_agent",
    system_message=sql_query_generator_prompt,
    llm_config={
        "config_list": config_list,
    },
)

# Define the Group Chat with the agents
groupchat = autogen.GroupChat(
    agents=[user_proxy, fetcher_agent, job_desc_creator_agent, email_agent, executor_agent, sql_query_generator_agent],
    messages=[],
    max_round=50,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
})

# Initiate the conversation with the User Proxy
def initiate_chat():
    user_proxy.initiate_chat(manager, message=f"""Process overview:
                                        There are 4 agents:
                                        1. Candidate Fetching Agent: Responsible for retrieving the top candidates for a given job ID.
                                        2. Function Executor Agent: Executes all functions for the group.
                                        3. Job Description Generator Agent: Generates a comprehensive job description using the information provided.
                                        4. Email Service Agent: Sends emails as per the group conversation.
                             
                                        When user requests a task, then only the appropriate agent will answer.
                                        - For example if user asks to fetch top candidates, then only Candidate Fetching Agent will answer.
                                        - If user asks to generate job description, then only Job Description Generator Agent will answer. 
                                        - If user asks to send emails, then only Email Service Agent will answer.   

                                        General Instructions:
                                        - there are going to be cases where the agents will ask for more information or clarification.
                                        - there are going to be cases when the execution of one function or agent will depend on the output of another function or agent. Ensure that these also are handled properly.                       
                                        """)



