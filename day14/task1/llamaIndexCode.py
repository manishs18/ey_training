from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 🟢 2. LlamaIndex Example (Document Q&A)

# Load documents
documents = SimpleDirectoryReader("policies").load_data()

# Build index
index = VectorStoreIndex.from_documents(documents)

# Query engine
query_engine = index.as_query_engine()

response = query_engine.query("What is delivery policy?")

print(response)