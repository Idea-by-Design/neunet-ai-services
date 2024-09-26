import autogen
import os
import uuid
from dotenv import load_dotenv
import json
from common.database.cosmos.db_operations import fetch_application_by_job_id,  fetch_application_by_job_id, create_application_for_job_id, save_ranking_data_to_cosmos_db


def initiate_chat(job_id, job_questionnaire_id, resume, job_description, candidate_email, job_questionnaire):

    # Load the .env file
    load_dotenv()

    # Fetching the API key from the environment variable
    api_key='sk-WVMOT-ux9F3MYCBpJdCTqCwjPfyCQa-iGBwD7yJtkST3BlbkFJyDQSA4BntLqFwINg-xRxS3DAsAbTbvlH5Cs2iUr2EA'

    # Use the job_questionnaire that is passed as an argument
    questionnaire = job_questionnaire

    # Terminates the conversation if the message is "TERMINATE"
    def is_termination_msg(message):
        has_content = "content" in message and message["content"] is not None
        return has_content and "TERMINATE" in message["content"]

    import json

    def create_json_safe_payload(data):
        try:
            # Convert the data to a JSON-compatible string
            return json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            print(f"Error creating JSON payload: {e}")
            return None
    
    

    # Ranking tool function
    def ranking_tool(candidate_email, ranking, conversation, resume, job_description):
        try:
            # Sanitize all inputs to avoid JSON errors
            candidate_email_safe = create_json_safe_payload(candidate_email)
            resume_safe = create_json_safe_payload(resume)
            job_description_safe = create_json_safe_payload(job_description)
            conversation_safe = create_json_safe_payload(conversation)

            if not all([candidate_email_safe, resume_safe, job_description_safe, conversation_safe]):
                print("Error: One or more payload fields could not be converted to JSON-safe format.")
                return "Payload creation failed due to special characters."

            # Fetch the application data from Cosmos DB using job_id
            ranking_data = fetch_application_by_job_id(job_id)

            # If no ranking data is found, create a new application
            if not ranking_data:
                ranking_data = create_application_for_job_id(job_id, job_questionnaire_id)

            # Generate a unique ID for the ranking entry (using job_id and job_questionnaire_id)
            unique_id = f"{job_id}_{job_questionnaire_id}_{str(uuid.uuid4())}"

            # Update the ranking data with the new entry
            ranking_data[candidate_email_safe] = {
                "Unique_id": unique_id,
                "ranking": ranking,
                "conversation": conversation_safe,
                "resume": resume_safe,
                "job_description": job_description_safe
            }

            # Save or update the ranking data in Cosmos DB
            save_ranking_data_to_cosmos_db(ranking_data)

            return f"Ranking entry saved with unique ID: {unique_id} for candidate email: {candidate_email_safe}"

        except Exception as e:
            print(f"An error occurred in the ranking tool: {e}")
            return None



    


    # User proxy (The user proxy is the main object that you will use to interact with the assistant)
    user_proxy = autogen.UserProxyAgent(name="user_proxy", system_message="You're the hiring manager", 
                                        human_input_mode="NEVER", is_termination_msg=is_termination_msg, 
                                        function_map={"ranking_tool": ranking_tool}, 
                                        code_execution_config={"use_docker": False})

    # Resume analysis agent to analyze the resume
    resume_analyst = autogen.AssistantAgent(name="resume_analyst", system_message="""
                                            
                                                Task Overview: You are tasked with scoring resumes based on a questionnaire that assesses various aspects of a candidate’s experience. 
                                                You need to score all Questions at once in one go.
                                                Each question in the questionnaire carries a specific weight, and candidates are given a score of 0, 1, or 2 depending on their level of experience. 
                                                Your goal is to calculate a final weighted score total by aggregating the scores from all sections.

                                                Scoring Instructions:
                                                For each question, assign a score based on the candidate’s experience:
                                                2 points for direct experience or strong evidence.
                                                1 point for related experience or partial evidence.
                                                0 points for no experience or no relevant evidence.
                                                Multiply the score by the weight of the question to calculate the weighted score for that question.

                                                Candidate score: Sum the weighted scores for all questions across all sections to get the total weighted score.
                                                Total Possible Score: The maximum possible score is the sum of highest score for that question (i.e. 2) multiplied weight of that question for all questions across all sections.

                                                Normalize the final total score by dividing the Candidate score by the Total Possible Score and express this as a percentage.
                                                                                            
                                            """,
                                            llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}], 
                                                        "max_tokens": 2000})

    # Job description analysis agent to analyze the job description and refer to the questionnaire
    job_description_analyst = autogen.AssistantAgent(name="job_description_analyst", system_message=f"""As the job description analysis agent,
                                                    you will ask relevant questions based on the job questionnaire to assess the candidate's fit. Here are the questions from the job questionnaire:
                                                    {questionnaire}
                                                    Show the questionnaire to resume analyst with questions, weight, scoring options.
                                                    Ask the resume analyst to score the resume based on the questionnaire in one go.
                                                    """,
                                                    llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}], 
                                                                "max_tokens": 2000})

    # Ranking tool declaration
    ranking_tool_declaration = {
        "name": "ranking_tool",
        "description": "Provides a ranking based on the conversation between the resume analyst and job description analyst.",
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_email": {"type": "string", "description": "The email of the candidate"},
                "ranking": {"type": "number", "description": "The ranking value"},
                "conversation": {"type": "string", "description": "The conversation"},
                "resume": {"type": "string", "description": "The resume"},
                "job_description": {"type": "string", "description": "The job description"}
            },
            "required": ["candidate_email", "ranking", "conversation", "resume", "job_description"]
        }
    }

    # Ranking agent to provide a ranking based on the conversation
    ranking_agent = autogen.AssistantAgent(name="ranking_agent", system_message="""As the ranking agent, you provide a ranking
                                        based on the scoring provided by resume analyst.""",
                                        llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}],  
                                                    "max_tokens": 4096,
                                                    "functions": [ranking_tool_declaration]})

    # Group chat among the agents
    group_chat = autogen.GroupChat(agents=[user_proxy, job_description_analyst, resume_analyst, ranking_agent], messages=[])

    # Manager to manage the group chat
    group_chat_manager = autogen.GroupChatManager(groupchat=group_chat, llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}]})

    # Initiate the group chat and feed in the questionnaire for job_description_analyst to ask
    user_proxy.initiate_chat(group_chat_manager,
                             message=f"""Process overview:
                                        1. Job description analyst will show the complete questionnaire to resume analyst.
                                        2. Resume analyst analyzes the resume and scores all questions at once in one go. 
                                        3. Ranking agent provides a ranking based on the responses.
                                        Resume: {resume}
                                        Job Description: {job_description}
                                        Candidate mail: {candidate_email}
                                        """
                             )
