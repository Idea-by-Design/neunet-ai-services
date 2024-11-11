import autogen
import os
from common.database.cosmos.db_operations import fetch_top_k_candidates_by_count, fetch_top_k_candidates_by_percentage

# Fetch the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")


# Configuration for AI models
config_list = [{"model": "gpt-4o", "api_key": api_key}]

# Define the User Proxy Agent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"use_docker": False}
)

# Define the Executor Agent to run functions
executor_agent_prompt = '''
This agent executes all functions for the group. 
It receives function requests from other agents and runs them with the provided arguments.
'''
executor_agent = autogen.AssistantAgent(
    name="function_executor_agent",
    system_message=executor_agent_prompt,
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "fetch_top_k_candidates_by_percentage",
                "description": "Fetches the top percentage of candidates (email and ranking only) for a given job ID.",
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
            }
        ]
    },
)


# Register the functions with the executor agent
executor_agent.register_function(
    function_map={
        "fetch_top_k_candidates_by_percentage": fetch_top_k_candidates_by_percentage,
        "fetch_top_k_candidates_by_count": fetch_top_k_candidates_by_count,
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

# Define the Group Chat with the agents
groupchat = autogen.GroupChat(
    agents=[user_proxy, fetcher_agent, executor_agent, job_desc_creator_agent],
    messages=[],
    max_round=50,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
})

# Initiate the conversation with the User Proxy
def initiate_chat():
    user_proxy.initiate_chat(manager, message=f"""Process overview:
                                        There are 3 agents:
                                        1. Candidate Fetching Agent: Responsible for retrieving the top candidates for a given job ID.
                                        2. Function Executor Agent: Executes all functions for the group.
                                        3. Job Description Generator Agent: Generates a comprehensive job description using the information provided.
                             
                                        When user requests a task, then only the appropriate agent will answer.
                                        For example if user asks to fetch top candidates, then only Candidate Fetching Agent will answer.
                                        If user asks to generate job description, then only Job Description Generator Agent will answer.                           
                                        """)


# Start the chat
initiate_chat()
