import autogen
import os
from common.database.cosmos.db_operations import fetch_top_k_candidates_by_job_id

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
                "name": "fetch_top_k_candidates_by_job_id",
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
            }
        ]
    },
)


# Register the functions with the executor agent
# Register the single function with the executor agent
executor_agent.register_function(
    function_map={
        "fetch_top_k_candidates_by_job_id": fetch_top_k_candidates_by_job_id,
    }
)




# Define the Fetcher Agent
fetcher_agent_prompt = '''
This agent is responsible for fetching the top percentage of candidates for a given job ID.
It will ask the executor agent to run the function `fetch_top_k_candidates_by_job_id`, which fetches both the candidate data and sorts it to return the top percentage.
Once the information is fetched, it will print the top candidates' email IDs and rankings.
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
