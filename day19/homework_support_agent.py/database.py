from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import RedisChatMessageHistory
import config

# Initialize Long-Term Vector Memory
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma(embedding_function=embeddings, persist_directory=config.CHROMA_DIR)

def get_short_term_history(session_id: str) -> RedisChatMessageHistory:
    """Helper to fetch or instantiate fluid conversation states from Redis."""
    return RedisChatMessageHistory(session_id=session_id, url=config.REDIS_URL)