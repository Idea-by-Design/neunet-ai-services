import os

# Fetch the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

name_to_account_id = {
    "Alice": "A123",
    "Bob": "B456",
    "Charlie": "C789"
}

account_id_to_bill = {
    "A123": 120.50,
    "B456": 200.75,
    "C789": 99.99
}

def get_account_id(name):
    return name_to_account_id.get(name, "Name not found")

def get_last_bill_amount(account_id):
    return account_id_to_bill.get(account_id, "Account ID not found")



import autogen
config_list = [{"model": "gpt-4o", "api_key": api_key}]


llm_config = {
    "config_list": config_list,
    "seed": 42,
    "functions":[
        {
            "name": "get_account_id",
            "description": "retrieves the account id for a user given their name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":{
                        "type": "string",
                        "description": "The name of the customer that will be used to lookup the account id"
                    }
                },
                "required":["name"]
            }
        },
        {
            "name": "get_last_bill_amount",
            "description": "Retrieves the last bill amount for a user for a given account id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id":{
                        "type": "string",
                        "description": "The account id fetched from get_account_id that will be used to lookup the last bill for the customer"
                    }
                },
                "required":["account_id"]
            }
        }
    ]
}

billing_assistant_agent_prompt = '''
This agent is a helpful assistant that can retrieve the account id and the last bill amount for a customer. 
Any other customer care requests are outside the scope of this agent. 
Once you have completed assisting the user output TERMINATE'''

billing_assistant_agent = autogen.AssistantAgent(
    name="billing_assistant_agent",
    system_message=billing_assistant_agent_prompt,
    llm_config=llm_config,
)


function_executor_agent_prompt = '''
This agent executes all functions for the group. 
Anytime an agent needs information they will prompt this agent with the indicated function and arguments.
'''
function_executor_agent = autogen.AssistantAgent(
    name="function_executor_agent",
    system_message=function_executor_agent_prompt,
    llm_config=llm_config,
)
function_executor_agent.register_function(
    function_map={
        "get_account_id": get_account_id,
        "get_last_bill_amount": get_last_bill_amount,
    }
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"use_docker": False}

)


groupchat = autogen.GroupChat(agents=[user_proxy, billing_assistant_agent, function_executor_agent], messages=[], max_round=50)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
})


user_proxy.initiate_chat(manager, message="Hello!")