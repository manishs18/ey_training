import os

# OpenAI & Tracing Setup
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "your-langsmith-key-here")

# Infrastructure Connections
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER = REDIS_URL
CELERY_BACKEND = REDIS_URL

CHROMA_DIR = "./chroma_db"