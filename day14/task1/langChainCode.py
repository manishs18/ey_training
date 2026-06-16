from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings


# 🟡 1. LangChain Example (Agent + RAG)

# Embeddings
embeddings = HuggingFaceEmbeddings()

# Vector DB
db = FAISS.load_local("policy_index", embeddings)

# LLM
llm = ChatOpenAI(model="gpt-4")

# RAG Pipeline
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever()
)

query = "What is refund policy?"
response = qa_chain.run(query)

print(response)