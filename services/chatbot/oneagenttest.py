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
-If the user requests candidates by count, call the executor to run fetch_top_k_candidates_by_count.
-If the request is by percentage, call the executor to run fetch_top_k_candidates_by_percentage.
-For non-standard requests (e.g., total number of candidates):
    Improvise by using available functions creatively. For instance, if the user wants the total number of candidates, run the fetch_top_k_candidates_by_percentage function with 100% and count the results.
-If no function can fulfill the request, inform the user that only count or percentage-based fetching is supported and suggest alternatives.

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

# Define the Group Chat with the agents
groupchat = autogen.GroupChat(
    agents=[user_proxy, fetcher_agent, executor_agent],
    messages=[],
    max_round=50,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
})

# Initiate the conversation with the User Proxy
def initiate_chat():
    user_proxy.initiate_chat(manager, message="Hello!")


# Start the chat
initiate_chat()
