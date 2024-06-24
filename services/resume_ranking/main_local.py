
import autogen
import os
import json
import uuid
from dotenv import load_dotenv

def initiate_chat(resume, job_description, canditate_mail):   

    # Load the .env file
    load_dotenv()

    # Fetching the API key from the environment variable
    api_key = os.getenv("OPENAI_API_KEY")

    # config_list is a list of dictionaries where each dictionary contains the model name and the API key
    config_list = [{"model":"gpt-3.5-turbo", "api_key":api_key}]

    # Terminates the conversation if the message is "TERMINATE" 
    def is_termination_msg(message):
        has_content = "content" in message and message["content"] is not None
        return has_content and "TERMINATE" in message["content"]
    
    
    # Ranking tool function
    def ranking_tool(canditate_mail, ranking , conversation, resume,  job_description):
        
        # Load the existing ranking data from the JSON file
        ranking_data = load_ranking_data()
        
        # Generate a unique ID for the ranking entry
        unique_id = str(uuid.uuid4())
        
        # Update the ranking data with the new entry
        ranking_data[canditate_mail] = {
            "Unique_id": unique_id,  # just in case if they have multiple applications but not trivial so used email as key but can be changed according to the requirement
            "ranking": ranking,
            "conversation": conversation,
            "resume": resume,
            "job_description": job_description
        }
        
        # Save the updated ranking data to the JSON file
        save_ranking_data(ranking_data)
        
        return f"Ranking entry saved with unique ID: {unique_id}"

    # Load the ranking data from the JSON file
    def load_ranking_data():
        if os.path.exists("ranking_data.json"):
            with open("ranking_data.json", "r") as file:
                return json.load(file)
        else:
            return {}

    # Save the ranking data to the JSON file
    def save_ranking_data(ranking_data):
        with open("ranking_data.json", "w") as file:
            json.dump(ranking_data, file)


    # User proxy (The user proxy is the main object that you will use to interact with the assistant its like proxy to human)
    user_proxy = autogen.UserProxyAgent(name="user_proxy", system_message="You're the hiring manager", human_input_mode="NEVER",
                                        is_termination_msg=is_termination_msg, function_map={"ranking_tool": ranking_tool},
                                                                            code_execution_config={"use_docker": False})

    # Resume analysis agent to analyze the resume
    resume_analyst = autogen.AssistantAgent(name="resume_analyst", system_message="""As the resume analysis agent,
                                            you are responsible for analyzing the resume and answering questions about the candidate's skills and experience.
                                            Try to capture the inner meaning of the resume, as skills may not always be straightforward.""",
                                            llm_config={"config_list": config_list, "max_tokens": 300})

    # Job description analysis agent to analyze the job description
    job_description_analyst = autogen.AssistantAgent(name="job_description_analyst", system_message="""As the job description analysis agent,
                                                    you are responsible for analyzing the job description and asking relevant questions to the resume analyst
                                                    to determine if the candidate meets the job requirements.""",
                                                    llm_config={"config_list": config_list, "max_tokens": 300})

    # Ranking tool declaration
    ranking_tool_declaration = {
        "name": "ranking_tool",
        "description": "Provides a ranking based on the conversation between the resume analyst and job description analyst with candidatename, ranking, conversation, resume, and job description as input parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_name": {
                    "type": "string",
                    "description": "The name of the candidate"
                },
            "ranking": {
                    "type": "number",
                    "description": "The ranking value provided by the ranking agent"
                },
                "conversation": {
                    "type": "string",
                    "description": "The conversation between the resume analyst and job description analyst"
                },

                "resume": {
                    "type": "string",
                    "description": "The resume of the candidate"
                },
                "job_description": {
                    "type": "string",
                    "description": "The job description"
                }
                
                
            },
            "required": ["candidate_name", "ranking", "conversation", "resume", "job_description"]
        },
    }


    # Ranking agent to provide a ranking based on the conversation
    ranking_agent = autogen.AssistantAgent(name="ranking_agent", system_message="""As the ranking agent, you are responsible for providing a ranking
                                        based on the conversation between the resume analyst and job description analyst. Use a scale of 0.0000 to 9.9999.
                                        """,
                                        llm_config={"config_list": config_list, "functions": [ranking_tool_declaration]})


    # Group chat among the agents
    group_chat = autogen.GroupChat(agents=[user_proxy, resume_analyst, job_description_analyst, ranking_agent], messages=[])

        # Manager to manage the group chat
    group_chat_manager = autogen.GroupChatManager(groupchat=group_chat, llm_config={"config_list": config_list})
    
    # Initiate the group chat
    user_proxy.initiate_chat(group_chat_manager,
                             message=f"""Process overview:
                                        Step 1. Resume analyst analyzes the resume and answers questions about the candidate's skills and experience.
                                        
                                        Step 2. Job description analyst analyzes the job description and asks relevant questions to the resume analyst.
                                        
                                        Step 3: Both will have a conversation like five question and answers to determine if the candidate meets the job requirements.
                                        
                                        Step 4. Ranking agent provides a ranking based on the conversation and add it to the ranking file for future reference.
                                        
                                        Resume: {resume}
                                        Job Description: {job_description}
                                        Candidate mail: {candidate_mail}
                                        """
                             )

if __name__ == "__main__":
    # Placeholders for input
    resume = "RESUME_PLACEHOLDER"
    job_description = "JOB_DESCRIPTION_PLACEHOLDER"
    candidate_mail = "CANDIDATE_EMAIL_PLACEHOLDER"
    
    initiate_chat(resume, job_description, candidate_mail)