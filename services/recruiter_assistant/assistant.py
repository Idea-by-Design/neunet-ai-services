from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.document_loaders import WebBaseLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain.utilities import ArxivAPIWrapper
from langchain.tools import ArxivQueryRun
from langchain import hub
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain.llms import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

# Set the OpenAI API key as an environment variable
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Create an instance of the WikipediaAPIWrapper class with the top result and a maximum of 200 characters for each document
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)

# Create an instance of the WikipediaQueryRun class using the WikipediaAPIWrapper instance
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

# Create a WebBaseLoader instance with the URL of the website to be loaded
loader = WebBaseLoader("https://example.com")  # Replace with the relevant website URL

# Load the documents from the specified website
docs = loader.load()

# Split the loaded documents into chunks of 1000 characters with an overlap of 200 characters
documents = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

# Create a FAISS database from the split documents using OpenAIEmbeddings
vectordb = FAISS.from_documents(documents, OpenAIEmbeddings())

# Create a retriever from the FAISS database
retriever = vectordb.as_retriever()

# Tools for the agent to use

# Wikipedia tool for the agent to use to search for information
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

# Tool for the agent to use to search for information about the application
retriever_tool = create_retriever_tool(retriever, "App_search",
                                        "Search for information about the application. For any questions related to the application, you must use this tool!")

# Arxiv tool for the agent to use to search for information
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

# Tool kit for the agent to use
tools = [wiki, retriever_tool, arxiv]

# Create an LLM instance and prompt template
llm = OpenAI(model="gpt-3.5-turbo", temperature=0)

# Default prompt can be changed to any prompt
prompt = hub.pull("hwchase17/openai-functions-agent")

# Create an agent with the tools and the LLM instance
agent = create_openai_tools_agent(llm, tools, prompt)

# Agent executor to run the agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Example usage
result = agent_executor.invoke({"What can I do as a recruiter on this platform?"})
print(result)