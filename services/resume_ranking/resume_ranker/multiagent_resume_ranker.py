import autogen
import os
import uuid
import json
from common.database.cosmos.db_operations import fetch_application_by_job_id,  fetch_application_by_job_id, create_application_for_job_id, save_ranking_data_to_cosmos_db


def initiate_chat(job_id, job_questionnaire_id, resume, job_description, candidate_email, job_questionnaire):


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
    def ranking_tool(candidate_email, ranking, conversation, resume):
        try:
            # Sanitize all inputs to avoid JSON errors
            candidate_email_safe = create_json_safe_payload(candidate_email)
            resume_safe = create_json_safe_payload(resume)
            conversation_safe = create_json_safe_payload(conversation)

            if not all([candidate_email_safe, resume_safe, conversation_safe]):
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
    
    
    # Job description analysis agent to analyze the job description and refer to the questionnaire
    job_description_analyst = autogen.AssistantAgent(name="job_description_analyst", system_message=f"""As the job description analysis agent,
                                                    you will ask relevant questions based on the job questionnaire to assess the candidate's fit. Here are the questions from the job questionnaire:
                                                    {questionnaire} 
                                                    Show the questionnaire to resume analyst with questions, weights.
                                                    Ask the resume analyst to use its scoring mechanism and score the resume based on the questionnaire in one go.
                                                    """,
                                                    llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}], 
                                                                "max_tokens": 2000})
    
    
    # Resume analysis agent to analyze the resume
    resume_analyst = autogen.AssistantAgent(name="resume_analyst", system_message="""

                                                                    Task Overview: You are tasked with scoring resumes based on a questionnaire that assesses various aspects of a candidate’s experience.
                                                                    You need to score all questions at once in one go.
                                                                    Each question in the questionnaire carries a specific weight, and candidates are scored based on their experience level and the company they have worked for.
                                                                    Your goal is to calculate a final weighted score total by aggregating the scores from all sections.

                                                                    Persona:
                                                                    You are a seasoned hiring consultant with over 30 years of experience evaluating candidates across a wide range of industries and company sizes. You have seen tens of thousands of resumes throughout your career and have a deep understanding of what differentiates average candidates from exceptional ones. You have worked with entry-level to C-suite candidates, assessing their skills, experiences, and potential contributions to companies. 

                                                                    You are unbiased and methodical in your evaluations. You have a keen eye for details and can quickly spot discrepancies, exaggerations, or understatements in resumes. You critically analyze each resume without allowing personal preferences or biases to influence your scoring. You are fair, honest, and known for scoring accurately, ensuring that exceptional candidates are rewarded for their achievements, while average candidates are not over-scored. You are also not afraid to penalize candidates where necessary, ensuring that only the most qualified rise to the top.

                                                                    Scoring Instructions:
                                                                    For each question, assign a score based on the candidate’s experience using the following criteria:

                                                                    1. Expert-Level Relevant Experience with Big or Well-Known Companies:
                                                                    Score: 5
                                                                    Candidates who have expert-level experience in relevant skills or domains, and who have worked at prestigious, well-known companies in the industry.

                                                                    2. Expert-Level Relevant Experience with Small or Not-So-Well-Known Companies:
                                                                    Score: 4
                                                                    Candidates who have expert-level experience in relevant skills or domains, but have worked at smaller or lesser-known companies in the industry.

                                                                    3. Transferable Skills with Big or Well-Known Companies:
                                                                    Score: 3
                                                                    Candidates who have transferable skills from a well-known company that may be applied to the role but are not directly relevant.

                                                                    4. Transferable Skills with Small or Not-So-Well-Known Companies:
                                                                    Score: 2
                                                                    Candidates who have transferable skills from a lesser-known company that may be applied to the role but are not directly relevant.

                                                                    5. Some Relevance to the Job Requirements:
                                                                    Score: 1
                                                                    Candidates who have some relevant experience or skills but lack significant depth or alignment with the job.

                                                                    6. No Experience or Not Relevant:
                                                                    Score: 0
                                                                    Candidates who have no relevant experience or skills aligned with the job requirements.

                                                                    Bonus Points:
                                                                    +1: Candidates who exceed expectations by demonstrating exceptional leadership, innovation, industry awards, or contributions in prestigious companies that are not necessarily listed in the job description but add significant value.
                                                                
                                                                    Critical Scoring Approach:
                                                                    - Apply your 30 years of experience to discern the difference between genuinely exceptional resumes and those that are simply average.
                                                                    - Be thorough and exacting in your scoring. If a candidate is overstating or lacks strong evidence, appropriately penalize them.
                                                                    - Score honestly, rewarding candidates for exceptional achievements but avoiding leniency for those who fail to meet the standards.

                                                                    Sample Output format for each question:
                                                                    
                                                                    {
                                                                        "question": " <the question as mentioned in questionnaire>",
                                                                        "weight": <the weight of question>,
                                                                        "scoring": " <Your score for this question>"
                                                                        "reasoning": " <Your reasoning for the score>"
                                                                    }
                                                                    
                                                                                 
                                                                    Once you complete your task, give the questionnaire output to score_calculator_analyst agent and it to calculate the final score.
                                                                    """,
                                            llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}], 
                                                        "max_tokens": 4096})

    
    # Job description analysis agent to analyze the job description and refer to the questionnaire
    score_calculator_analyst = autogen.AssistantAgent(name="score_calculator_analyst", system_message = f"""
                                                                Your task is to accurately calculate the final weighted and normalized score from the questionnaire responses.

                                                                1. **Input Validation**:
                                                                - Ensure that each question has a valid score (between 0 and 5) and a valid weight (non-negative).
                                                                - If any score or weight is missing or invalid, raise an error and skip to the next valid question.

                                                                2. **Candidate Score Calculation**:
                                                                - For each valid question:
                                                                    - Multiply the response score by the corresponding question weight to calculate the weighted score.
                                                                    - **Validation**: Ensure that the weighted score for each question does not exceed the maximum possible weighted score for that question (i.e., 5 multiplied by the question's weight).
                                                                - Sum all validated weighted scores across all sections to obtain the **Candidate's Total Score**.

                                                                3. **Total Possible Score Calculation**:
                                                                - For each question, calculate the maximum possible score by multiplying the highest possible score (e.g., 5) by the weight of that question.
                                                                - Sum all maximum possible scores across all sections to obtain the **Total Possible Score**.
                                                                - **Validation**: Ensure the Total Possible Score is non-zero and valid. If it's zero or invalid, return an error.

                                                                4. **Final Score Calculation**:
                                                                - Normalize the candidate’s total score by dividing the **Candidate's Total Score** by the **Total Possible Score**.
                                                                - **Validation**: Ensure the normalized score is within the valid range (0% to 100%).
                                                                    - If the normalized score exceeds 100%, recalculate the score and correct it based on the validated weights and scores.
                                                                    - **Validation**: Ensure that no rounding or precision errors lead to a score greater than 100%.

                                                                5. **Output**:
                                                                - Return the candidate’s validated and corrected final weighted normalized score as a percentage (between 0% and 100%).
                                                                - If any errors or inconsistencies occur, clearly state them and indicate which steps failed.

                                                                Make sure every calculation and validation is done carefully to avoid any incorrect results.
                                                                """,
                                                    llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}], 
                                                                "max_tokens": 2000})
    
    # Ranking tool declaration
    ranking_tool_declaration = {
        "name": "ranking_tool",
        "description": "Provides a ranking based on the calculation given by score_calculator_analyst.",
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_email": {"type": "string", "description": "The email of the candidate"},
                "ranking": {"type": "number", "description": "The ranking value"},
                "conversation": {"type": "string", "description": "The output of resume analyst"},
                "resume": {"type": "string", "description": "The resume"}
            },
            "required": ["candidate_email", "ranking", "conversation", "resume"]
        }
    }

    # Ranking agent to provide a ranking based on the conversation
    ranking_agent = autogen.AssistantAgent(name="ranking_agent", system_message="""As the ranking agent, you provide a ranking
                                        based on the scoring provided by score_calculator_analyst.""",
                                        llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}],  
                                                    "max_tokens": 4096,
                                                    "functions": [ranking_tool_declaration]})

    # Group chat among the agents
    group_chat = autogen.GroupChat(agents=[user_proxy, job_description_analyst, resume_analyst, score_calculator_analyst, ranking_agent], messages=[])

    # Manager to manage the group chat
    group_chat_manager = autogen.GroupChatManager(groupchat=group_chat, llm_config={"config_list": [{"model":"gpt-4o-mini", "api_key":api_key}]})

    # Initiate the group chat and feed in the questionnaire for job_description_analyst to ask
    user_proxy.initiate_chat(group_chat_manager,
                             message=f"""Process overview:
                                        1. Job description analyst will show the complete questionnaire to resume analyst as provided in its instructions.
                                        2. Resume analyst analyzes the resume and scores all questions at once in one go as provided in its instructions. 
                                        3. Score calculator analyst calculates the final weighted score total by aggregating the scores from all sections as provided in its instructions.
                                        4. Ranking agent provides a ranking based on the responses as provided in its instructions.
                                        
                                        Job Description: {job_description} 
                                        
                                        Here is the Candidate information
                                        Candidate mail: {candidate_email}
                                        Resume: {resume}                                      
                                        """
                             )
