import autogen
from common.database.cosmos.db_operations import fetch_application_by_job_id, fetch_top_candidates_from_results
import os

# Fetch API key from environment
api_key = 'sk-WVMOT-ux9F3MYCBpJdCTqCwjPfyCQa-iGBwD7yJtkST3BlbkFJyDQSA4BntLqFwINg-xRxS3DAsAbTbvlH5Cs2iUr2EA'

# Configuration for AI models
config_list = [{"model": "gpt-4o", "api_key": api_key}]

# Define the User Proxy Agent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"use_docker": False}
)

# Define the Top Candidate Fetcher Agent
fetcher_agent_prompt = '''
This agent is responsible for fetching the top percentage of candidates for a given job ID.
It will receive a job ID and the required percentage and will fetch the information from the database.
Once the information is fetched, it will print the top candidates' names, rankings, and email IDs.
After completing the task, it will output TERMINATE.
'''
fetcher_agent = autogen.AssistantAgent(
    name="top_candidate_fetcher",
    system_message=fetcher_agent_prompt,
    llm_config={
        "config_list": config_list,
        "seed": 42,
        "functions": [
            {
                "name": "fetch_application_by_job_id",
                "description": "Fetches the application data for a given job ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "number",
                            "description": "The job ID for which to fetch the application data."
                        }
                    },
                    "required": ["job_id"]
                }
            },
            {
                "name": "fetch_top_candidates_from_results",
                "description": "Fetches the top percentage of candidates from the given application data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "object",
                            "description": "The application data from which to fetch the top candidates."
                        },
                        "percentage": {
                            "type": "number",
                            "description": "The percentage of top candidates to fetch."
                        }
                    },
                    "required": ["results", "percentage"]
                }
            }
        ]
    },
)

# Register the functions with the fetcher agent
fetcher_agent.register_function(
    function_map={
        "fetch_application_by_job_id": fetch_application_by_job_id,
        "fetch_top_candidates_from_results": fetch_top_candidates_from_results,
    }
)

# Define the Group Chat with the agents
groupchat = autogen.GroupChat(
    agents=[user_proxy, fetcher_agent],
    messages=[],
    max_round=5,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
    "seed": 42,
})

# Initiate the conversation with the User Proxy
def initiate_chat():
    user_proxy.initiate_chat(manager, message="I want top 10% candidates for job ID 123486")

    # # Example of how the fetcher agent would process the request
    # job_id = 123486
    # percentage = 10
    # application_data = fetch_application_by_job_id(job_id)

    # if application_data:
    #     top_candidates = fetch_top_candidates_from_results(application_data, percentage)

    #     if top_candidates:
    #         for candidate in top_candidates:
    #             print(f"Name: {candidate['email']}, Ranking: {candidate['ranking']}, Email: {candidate['email']}")

    # Terminate the agent session
    print("TERMINATE")

# Start the chat
initiate_chat()
