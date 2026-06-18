import os
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
    openai_api_key=os.getenv("AZURE_API_KEY"),
    openai_api_version="2024-06-01",
    temperature=0
)