from haystack import Document
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.document_stores import FAISSDocumentStore


# 🔵 3. Haystack Example (Search Pipeline)
# Document store
document_store = FAISSDocumentStore()

# Retriever
retriever = EmbeddingRetriever(document_store=document_store)

# Pipeline
pipeline = ExtractiveQAPipeline(reader=None, retriever=retriever)

result = pipeline.run(
    query="What is cancellation policy?",
    params={"Retriever": {"top_k": 5}}
)

print(result)