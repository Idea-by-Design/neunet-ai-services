import autogen
import os
import logging
from typing import Dict, List, Optional, Any
from common.database.cosmos.db_operations import (
    fetch_top_k_candidates_by_count,
    fetch_top_k_candidates_by_percentage,
    update_application_status,
    execute_sql_query
)
from services.chatbot.functions import send_email
from ..prompts.multiagent_assistant_prompts import (
    executor_agent_system_message,
    fetcher_agent_system_message,
    email_agent_system_message,
    job_desc_creator_system_message,
    sql_query_generator_system_message,
    initiate_chat_system_message
)
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in the project directory
load_dotenv(dotenv_path=".env")

try:
    # Configuration for Azure OpenAI models
    config_list = [{
        "model": os.getenv("deployment_name"),
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_type": os.getenv("api_type"),
        "api_version": os.getenv("api_version")
    }]
except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    raise

class ChatManager:
    def __init__(self):
        try:
            # Define the User Proxy Agent
            self.user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=50,
                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                code_execution_config={"use_docker": False}
            )

            # Define the Executor Agent
            self.executor_agent = autogen.AssistantAgent(
                name="function_executor_agent",
                system_message=executor_agent_system_message,
                llm_config={
                    "config_list": config_list,
                    "functions": self._get_function_definitions()
                },
            )

            # Register functions with executor agent
            self.executor_agent.register_function(
                function_map=self._get_function_map()
            )

            # Define other agents
            self.fetcher_agent = autogen.AssistantAgent(
                name="top_candidate_fetcher",
                system_message=fetcher_agent_system_message,
                llm_config={"config_list": config_list},
            )

            self.email_agent = autogen.AssistantAgent(
                name="email_service_agent",
                system_message=email_agent_system_message,
                llm_config={"config_list": config_list},
            )

            self.job_desc_creator_agent = autogen.AssistantAgent(
                name="job_description_creator_agent",
                system_message=job_desc_creator_system_message,
                llm_config={"config_list": config_list},
            )

            self.sql_query_generator_agent = autogen.AssistantAgent(
                name="sql_query_generator_agent",
                system_message=sql_query_generator_system_message,
                llm_config={"config_list": config_list},
            )

            # Set up group chat
            self.groupchat = autogen.GroupChat(
                agents=[
                    self.user_proxy,
                    self.fetcher_agent,
                    self.job_desc_creator_agent,
                    self.email_agent,
                    self.executor_agent,
                    self.sql_query_generator_agent
                ],
                messages=[],
                max_round=50,
            )

            self.manager = autogen.GroupChatManager(
                groupchat=self.groupchat,
                llm_config={"config_list": config_list},
            )

        except Exception as e:
            logger.error(f"Error initializing ChatManager: {str(e)}")
            raise

    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get the function definitions for the executor agent"""
        return [
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
                        "count": {
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
                            "items": {"type": "string"},
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
                "description": "Executes the given SQL query generated by the sql_query_generator_agent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute."
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def _get_function_map(self) -> Dict[str, Any]:
        """Get the function map for the executor agent"""
        return {
            "fetch_top_k_candidates_by_percentage": fetch_top_k_candidates_by_percentage,
            "fetch_top_k_candidates_by_count": fetch_top_k_candidates_by_count,
            "send_email": send_email,
            "update_application_status": update_application_status,
            "execute_sql_query": execute_sql_query
        }

    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a message through the multi-agent system
        
        Args:
            message: The user's message
            
        Returns:
            Dict containing the response and any additional data
        """
        try:
            # Reset the chat for a new conversation
            self.manager.reset()
            
            # Initialize the conversation
            response = await self.user_proxy.a_initiate_chat(
                self.manager,
                message=message
            )
            
            # Extract the last response
            last_message = response.messages[-1] if response.messages else None
            content = last_message.get("content", "") if last_message else ""
            
            return {
                "status": "success",
                "response": content,
                "messages": response.messages
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "messages": []
            }

# Initialize the chat manager
chat_manager = ChatManager()
